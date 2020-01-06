# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import logging
from datetime import datetime

from redis import WatchError
from rq import get_current_job
from rq.job import Job, JobStatus, dumps, loads
from rq.utils import utcnow

from django.db import connection
from django.utils.encoding import iri_to_uri

from django_rq.queues import get_connection, get_queue

from pootle.core.cache import get_cache
from pootle.core.url_helpers import get_all_pootle_paths, split_pootle_path
from pootle.core.utils.timezone import datetime_min
from pootle_misc.util import dictsum


__all__ = ('TreeItem', 'CachedTreeItem', 'CachedMethods')


KEY_DIRTY_TREEITEMS = 'pootle:dirty:treeitems'
KEY_REFRESH_STATS = 'pootle:refresh:stats'
KEY_STATS_LAST_JOB_PREFIX = "pootle:stats:lastjob:"
KEY_STATS_JOB_PARAMS_PREFIX = "pootle:stats:job.params:"


logger = logging.getLogger('stats')
cache = get_cache('stats')


class NoCachedStats(Exception):
    pass


class CachedMethods(object):
    """Cached method names."""

    CHECKS = 'get_checks'
    WORDCOUNT_STATS = 'get_wordcount_stats'
    LAST_ACTION = 'get_last_action'
    SUGGESTIONS = 'get_suggestion_count'
    MTIME = 'get_mtime'
    LAST_UPDATED = 'get_last_updated'

    # Check refresh_stats command when add a new CachedMethod

    @classmethod
    def get_all(cls):
        return [getattr(cls, x) for x in
                filter(lambda x: x[:2] != '__' and x != 'get_all', dir(cls))]


class TreeItem(object):
    def __init__(self, *args, **kwargs):
        self._children = None
        self.initialized = False
        super(TreeItem, self).__init__()

    @property
    def cache_key(self):
        return self.pootle_path

    def get_children(self):
        """This method will be overridden in descendants"""
        return []

    def set_children(self, children):
        self._children = children
        self.initialized = True

    def get_parent(self):
        """This method will be overridden in descendants"""
        return None

    @classmethod
    def _get_wordcount_stats(cls):
        """This method will be overridden in descendants"""
        return {'total': 0, 'translated': 0, 'fuzzy': 0}

    @classmethod
    def _get_suggestion_count(cls):
        """This method will be overridden in descendants"""
        return 0

    @classmethod
    def _get_checks(cls):
        """This method will be overridden in descendants"""
        return {'unit_critical_error_count': 0, 'checks': {}}

    @classmethod
    def _get_last_action(cls):
        """This method will be overridden in descendants"""
        return {'mtime': 0}

    @classmethod
    def _get_mtime(cls):
        """This method will be overridden in descendants"""
        return datetime_min

    @classmethod
    def _get_last_updated(cls):
        """This method will be overridden in descendants"""
        return 0

    def is_dirty(self):
        """Checks if any of children is registered as dirty"""
        return any(map(lambda x: x.is_dirty(), self.children))

    def initialize_children(self):
        if self.initialized:
            return
        self._children = self.get_children()
        self.initialized = True

    @property
    def children(self):
        self.initialize_children()
        return self._children

    def _calc_suggestion_count(self):
        self.initialize_children()
        return (self._get_suggestion_count() +
                sum([item.get_cached(CachedMethods.SUGGESTIONS)
                     for item in self.children]))

    def _calc_wordcount_stats(self):
        result = self._get_wordcount_stats()
        self.initialize_children()
        for item in self.children:
            result = dictsum(
                result,
                item.get_cached(CachedMethods.WORDCOUNT_STATS)
            )

        return result

    def _calc_last_action(self):
        self.initialize_children()

        return max(
            [self._get_last_action()] +
            [item.get_cached(CachedMethods.LAST_ACTION)
             for item in self.children],
            key=lambda x: x['mtime'] if 'mtime' in x else 0
        )

    def _calc_mtime(self):
        """get latest modification time"""
        self.initialize_children()
        return max(
            [self._get_mtime()] +
            [item.get_cached(CachedMethods.MTIME)
             for item in self.children]
        )

    def _calc_last_updated(self):
        """get last updated"""
        self.initialize_children()
        return max(
            [self._get_last_updated()] +
            [item.get_cached(CachedMethods.LAST_UPDATED)
             for item in self.children],
        )

    def _calc_checks(self):
        result = self._get_checks()
        self.initialize_children()
        for item in self.children:
            item_res = item.get_cached(CachedMethods.CHECKS)
            result['checks'] = dictsum(result['checks'], item_res['checks'])
            result['unit_critical_error_count'] += \
                item_res['unit_critical_error_count']

        return result

    def get_stats(self, include_children=True):
        """Get stats for this particular tree item.

        Note objects using `TreeItem` don't have their own cached fields;
        these are aggregated based on the existing children stats. This
        is why children need to be unconditionally initialized.

        :param include_children: whether stats for children items should be
            included or not.
        """
        self.initialize_children()
        result = {
            'total': None,
            'translated': None,
            'fuzzy': None,
            'suggestions': None,
            'lastaction': None,
            'critical': None,
            'lastupdated': None,
            'is_dirty': self.is_dirty(),
        }

        try:
            result.update(self._calc_wordcount_stats())
        except NoCachedStats:
            pass

        try:
            result['suggestions'] = self._calc_suggestion_count()
        except NoCachedStats:
            pass

        try:
            result['lastaction'] = self._calc_last_action()
        except NoCachedStats:
            pass

        try:
            result['critical'] = self.get_error_unit_count()
        except NoCachedStats:
            pass

        try:
            result['lastupdated'] = self._calc_last_updated()
        except NoCachedStats:
            pass

        if include_children:
            result['children'] = [
                item.get_stats(include_children=False) for item in self.children
            ]

        return result

    def get_error_unit_count(self):
        check_stats = self._calc_checks()
        if check_stats is not None:
            return check_stats.get('unit_critical_error_count', 0)

        return None

    def get_checks(self):
        try:
            return self._calc_checks()['checks']
        except NoCachedStats:
            return None


class CachedTreeItem(TreeItem):
    def __init__(self, *args, **kwargs):
        self._dirty_cache = set()
        super(CachedTreeItem, self).__init__()

    def make_cache_key(self, name):
        return iri_to_uri('%s:%s' % (self.cache_key, name))

    def can_be_updated(self):
        """This method will be overridden in descendants"""
        return True

    def set_cached_value(self, name, value):
        return cache.set(self.make_cache_key(name), value, None)

    def get_cached_value(self, name):
        return cache.get(self.make_cache_key(name))

    def get_last_job_key(self):
        key = self.cache_key
        return KEY_STATS_LAST_JOB_PREFIX + key.replace("/", ".").strip(".")

    def update_cached(self, name):
        """calculate stat value and update cached value"""
        start = datetime.now()

        calc_fn = {
            CachedMethods.WORDCOUNT_STATS: self._calc_wordcount_stats,
            CachedMethods.SUGGESTIONS: self._calc_suggestion_count,
            CachedMethods.LAST_ACTION: self._calc_last_action,
            CachedMethods.LAST_UPDATED: self._calc_last_updated,
            CachedMethods.CHECKS: self._calc_checks,
            CachedMethods.MTIME: self._calc_mtime,
        }.get(name, lambda: None)

        self.set_cached_value(name, calc_fn())

        end = datetime.now()
        ctx = {
            'function': calc_fn.__name__,
            'time': end - start,
            'key': self.cache_key,
        }
        logger.debug('update_cached(%(function)s)\t%(time)s\t%(key)s', ctx)

    def get_cached(self, name):
        """get stat value from cache"""
        result = self.get_cached_value(name)
        if result is not None:
            return result

        logger.debug(
            u'Cache miss %s for %s(%s)',
            name, self.cache_key, self.__class__
        )
        raise NoCachedStats

    def get_checks(self):
        try:
            return self.get_cached(CachedMethods.CHECKS)['checks']
        except NoCachedStats:
            return None

    def get_stats(self, include_children=True):
        """Get stats for this particular tree item.

        :param include_children: whether stats for children items should be
            included or not.
        """
        if include_children:
            self.initialize_children()
        result = {
            'total': None,
            'translated': None,
            'fuzzy': None,
            'suggestions': None,
            'lastaction': None,
            'critical': None,
            'lastupdated': None,
            'is_dirty': self.is_dirty(),
        }

        try:
            result.update(self.get_cached(CachedMethods.WORDCOUNT_STATS))
        except NoCachedStats:
            pass

        try:
            result['suggestions'] = self.get_cached(CachedMethods.SUGGESTIONS)
        except NoCachedStats:
            pass

        try:
            result['lastaction'] = self.get_cached(CachedMethods.LAST_ACTION)
        except NoCachedStats:
            pass

        try:
            result['critical'] = self.get_error_unit_count()
        except NoCachedStats:
            pass

        try:
            result['lastupdated'] = self.get_cached(CachedMethods.LAST_UPDATED)
        except NoCachedStats:
            pass

        if include_children:
            result['children'] = [
                item.get_stats(include_children=False) for item in self.children
            ]

        return result

    def get_error_unit_count(self):
        check_stats = self.get_cached(CachedMethods.CHECKS)
        return check_stats.get('unit_critical_error_count', 0)

    def is_dirty(self):
        """Checks if current TreeItem is registered as dirty"""
        return self.get_dirty_score() > 0 or self.is_being_refreshed()

    def mark_dirty(self, *args):
        """Mark cached method names for this TreeItem as dirty"""
        for key in args:
            self._dirty_cache.add(key)

    def mark_all_dirty(self):
        """Mark all cached method names for this TreeItem as dirty"""
        self._dirty_cache = set(CachedMethods.get_all())

    def clear_cache(self):
        self.mark_all_dirty()

        keys = self._dirty_cache
        for key in keys:
            cache.delete(self.make_cache_key(key))

        if keys:
            logger.debug("%s deleted from %s cache", keys, self.cache_key)

        self._dirty_cache = set()

    # # # # # # #  Update stats in Redis Queue Worker process # # # # # # # #

    def all_pootle_paths(self):
        """Get cache_key for all parents (to the Language and Project)
        of current TreeItem
        """
        return get_all_pootle_paths(self.cache_key)

    def is_being_refreshed(self):
        """Checks if current TreeItem is being refreshed"""
        r_con = get_connection()
        path = r_con.get(KEY_REFRESH_STATS)

        if path is None:
            return False

        if path == '/':
            return True

        proj_code = split_pootle_path(path)[1]
        key = self.cache_key

        return key in path or path in key or key in '/projects/%s/' % proj_code

    def register_all_dirty(self):
        """Register current TreeItem and all parent paths as dirty
        (should be called before RQ job adding)
        """
        r_con = get_connection()
        for p in self.all_pootle_paths():
            r_con.zincrby(KEY_DIRTY_TREEITEMS, 1, p)

    def unregister_all_dirty(self, decrement=1):
        """Unregister current TreeItem and all parent paths as dirty
        (should be called from RQ job procedure after cache is updated)
        """
        r_con = get_connection()
        job = get_current_job()
        for p in self.all_pootle_paths():
            if job:
                logger.debug('UNREGISTER %s (-%s) where job_id=%s',
                             p, decrement, job.id)
            else:
                logger.debug('UNREGISTER %s (-%s)', p, decrement)
            r_con.zincrby(KEY_DIRTY_TREEITEMS, 0 - decrement, p)

    def unregister_dirty(self, decrement=1):
        """Unregister current TreeItem as dirty
        (should be called from RQ job procedure after cache is updated)
        """
        r_con = get_connection()
        job = get_current_job()
        if job:
            logger.debug('UNREGISTER %s (-%s) where job_id=%s',
                         self.cache_key, decrement, job.id)
        else:
            logger.debug('UNREGISTER %s (-%s)', self.cache_key, decrement)
        r_con.zincrby(KEY_DIRTY_TREEITEMS, 0 - decrement, self.cache_key)

    def get_dirty_score(self):
        r_con = get_connection()
        return r_con.zscore(KEY_DIRTY_TREEITEMS, self.cache_key)

    def update_dirty_cache(self):
        """Add a RQ job which updates dirty cached stats of current TreeItem
        to the default queue
        """
        _dirty = self._dirty_cache.copy()
        if _dirty:
            self._dirty_cache = set()
            self.register_all_dirty()
            create_update_cache_job_wrapper(self, _dirty)

    def update_all_cache(self):
        """Add a RQ job which updates all cached stats of current TreeItem
        to the default queue
        """
        self.mark_all_dirty()
        self.update_dirty_cache()

    def _update_cache_job(self, keys, decrement):
        """Update dirty cached stats of current TreeItem and add RQ job for
        updating dirty cached stats of parent
        """
        if self.can_be_updated():
            # children should be recalculated to avoid using of obsolete
            # directories or stores which could be saved in `children` property
            self.initialized = False
            self.initialize_children()
            keys_for_parent = set(keys)
            for key in keys:
                try:
                    self.update_cached(key)
                except NoCachedStats:
                    keys_for_parent.remove(key)

            if keys_for_parent:
                parent = self.get_parent()
                if parent is not None:
                    create_update_cache_job_wrapper(parent, keys_for_parent,
                                                    decrement)
                self.unregister_dirty(decrement)
            else:
                self.unregister_all_dirty(decrement)

        else:
            logger.warning('Cache for %s object cannot be updated.', self)
            self.unregister_all_dirty(decrement)


class JobWrapper(object):
    """
    Wraps RQ Job to handle it within external `watch`,
    encapsulates work with external to RQ job params which is needed
    because of possible race conditions
    """

    def __init__(self, id, connection):
        self.id = id
        self.func = None
        self.instance = None
        self.keys = None
        self.decrement = None
        self.depends_on = None
        self.origin = None
        self.timeout = None
        self.connection = connection
        self.job = Job(id=id, connection=self.connection)

    @classmethod
    def create(cls, func, instance, keys, decrement, connection, origin,
               timeout):
        """
        Creates object and initializes Job ID
        """
        job_wrapper = cls(None, connection)
        job_wrapper.job = Job(connection=connection)
        job_wrapper.id = job_wrapper.job.id
        job_wrapper.func = func
        job_wrapper.instance = instance
        job_wrapper.keys = keys
        job_wrapper.decrement = decrement
        job_wrapper.connection = connection
        job_wrapper.origin = origin
        job_wrapper.timeout = timeout

        return job_wrapper

    @classmethod
    def params_key_for(cls, id):
        """
        Gets Redis key for keeping Job params
        """
        return KEY_STATS_JOB_PARAMS_PREFIX + id

    def get_job_params_key(self):
        return self.params_key_for(self.id)

    def get_job_params(self):
        """
        Loads job params from Redis key
        """
        key = self.get_job_params_key()
        data = self.connection.get(key)
        if data is not None:
            return loads(data)
        return None

    def set_job_params(self, pipeline):
        """
        Sets dumped job params to Redis key
        """
        key = self.get_job_params_key()
        value = (self.keys, self.decrement)
        pipeline.set(key, dumps(value))

    def clear_job_params(self):
        """
        Removes job params key (used after job finishes)
        """
        key = self.get_job_params_key()
        self.job.connection.delete(key)

    def merge_job_params(self, keys, decrement, pipeline):
        """
        Merges job parameters to allow to skip one of these jobs
        """
        key = self.get_job_params_key()
        data = self.connection.get(key)
        old_keys, old_decrement = loads(data)
        new_params = (keys | old_keys, decrement + old_decrement)
        pipeline.set(key, dumps(new_params))

        return new_params

    def create_job(self, status=None, depends_on=None):
        """
        Creates Job object with given job ID
        """
        args = (self.instance,)
        return Job.create(self.func, args=args, id=self.id,
                          connection=self.connection, depends_on=depends_on,
                          status=status, origin=self.origin)

    def save_enqueued(self, pipe):
        """
        Preparing job to enqueue. Works via pipeline.
        Nothing done if WatchError happens while next `pipeline.execute()`.
        """
        job = self.create_job(status=JobStatus.QUEUED)
        self.set_job_params(pipeline=pipe)
        job.origin = self.origin
        job.enqueued_at = utcnow()
        if job.timeout is None:
            job.timeout = self.timeout
        job.save(pipeline=pipe)
        self.job = job

    def save_deferred(self, depends_on, pipe):
        """
        Preparing job to defer (add as dependent). Works via pipeline.
        Nothing done if WatchError happens while next `pipeline.execute()`.
        """
        job = self.create_job(depends_on=depends_on, status=JobStatus.DEFERRED)
        self.set_job_params(pipeline=pipe)
        job.register_dependency(pipeline=pipe)
        job.save(pipeline=pipe)

        return job


def update_cache_job(instance):
    """RQ job"""
    job = get_current_job()
    job_wrapper = JobWrapper(job.id, job.connection)
    keys, decrement = job_wrapper.get_job_params()

    # close unusable and obsolete connections before and after the job
    # Note: setting CONN_MAX_AGE parameter can have negative side-effects
    # CONN_MAX_AGE value should be lower than DB wait_timeout
    connection.close_if_unusable_or_obsolete()
    instance._update_cache_job(keys, decrement)
    connection.close_if_unusable_or_obsolete()

    job_wrapper.clear_job_params()


def create_update_cache_job_wrapper(instance, keys, decrement=1):
    queue = get_queue('default')
    if queue._is_async:

        def _create_update_cache_job():
            create_update_cache_job(queue, instance, keys, decrement=decrement)
        connection.on_commit(_create_update_cache_job)
    else:
        instance._update_cache_job(keys, decrement=decrement)


def create_update_cache_job(queue, instance, keys, decrement=1):
    queue.connection.sadd(queue.redis_queues_keys, queue.key)
    job_wrapper = JobWrapper.create(update_cache_job,
                                    instance=instance,
                                    keys=keys,
                                    decrement=decrement,
                                    connection=queue.connection,
                                    origin=queue.name,
                                    timeout=queue.DEFAULT_TIMEOUT)
    last_job_key = instance.get_last_job_key()

    with queue.connection.pipeline() as pipe:
        while True:
            try:
                pipe.watch(last_job_key)
                last_job_id = queue.connection.get(last_job_key)
                depends_on_wrapper = None
                if last_job_id is not None:
                    pipe.watch(Job.key_for(last_job_id),
                               JobWrapper.params_key_for(last_job_id))
                    depends_on_wrapper = JobWrapper(last_job_id,
                                                    queue.connection)

                pipe.multi()

                depends_on_status = None
                if depends_on_wrapper is not None:
                    depends_on = depends_on_wrapper.job
                    depends_on_status = depends_on.get_status()

                if depends_on_status is None:
                    # enqueue without dependencies
                    pipe.set(last_job_key, job_wrapper.id)
                    job_wrapper.save_enqueued(pipe)
                    pipe.execute()
                    break

                if depends_on_status in [JobStatus.QUEUED,
                                         JobStatus.DEFERRED]:
                    new_job_params = \
                        depends_on_wrapper.merge_job_params(keys, decrement,
                                                            pipeline=pipe)
                    pipe.execute()
                    logger.debug('SKIP %s (decrement=%s, job_status=%s, '
                                 'job_id=%s)', last_job_key, new_job_params[1],
                                 depends_on_status, last_job_id)
                    # skip this job
                    return None

                pipe.set(last_job_key, job_wrapper.id)

                if depends_on_status not in [JobStatus.FINISHED]:
                    # add job as a dependent
                    job = job_wrapper.save_deferred(last_job_id, pipe)
                    pipe.execute()
                    logger.debug('ADD AS DEPENDENT for %s (job_id=%s) OF %s',
                                 last_job_key, job.id, last_job_id)
                    return job

                job_wrapper.save_enqueued(pipe)
                pipe.execute()
                break
            except WatchError:
                logger.debug('RETRY after WatchError for %s', last_job_key)
                continue
    logger.debug('ENQUEUE %s (job_id=%s)', last_job_key, job_wrapper.id)

    queue.push_job_id(job_wrapper.id)
