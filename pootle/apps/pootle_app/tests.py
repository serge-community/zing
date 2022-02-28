from django.forms import model_to_dict
from django.test import TestCase
from django.core.management import call_command
from accounts.models import User
from pootle_app.models import Directory
from pootle_store.models import Store, Unit, Submission, Suggestion, QualityCheck
from pootle_translationproject.models import TranslationProject
from pootle_statistics.models import ScoreLog
from pootle_language.models import Language
import json
from pootle_project.models import Project


class CloneProjectCommandTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.PROJECT_ID = 4
        cls.RECORD_SEPARATOR = "------------------------"
        cls.TESTING_SEPARATOR = "\n**************************"

        system = User()
        system.email = "system@system.cl"
        system.username = "system"
        system.password = "123456"
        system.full_name = "systeeeeem"
        system.save()

        user_3130 = User()
        user_3130.username = "user123456"
        user_3130.email = "user@evernote.cl"
        user_3130.password = "123456111"
        user_3130.full_name = "usercompleted"
        user_3130.save()

        user_104795 = User()
        user_104795.username = "user104795"
        user_104795.email = "user104795@evernote.com"
        user_104795.password = "1234123124"
        user_104795.full_name = "usuario104795"
        user_104795.save()

        user_104788 = User()
        user_104788.username = "user104788"
        user_104788.email = "user104788@evernote.cl"
        user_104788.password = "13111111"
        user_104788.full_name = "completadouser"
        user_104788.save()

        directory_1 = Directory()
        directory_1.id = 1
        directory_1.parent = None
        directory_1.pootle_path = "/"
        directory_1.obsolete = 0
        directory_1.save()

        directory_2 = Directory()
        directory_2.id = 2
        directory_2.name = "projects"
        directory_2.parent = directory_1
        directory_2.pootle_path = "/projects/"
        directory_2.obsolete = 0
        directory_2.save()

        directory_138 = Directory()
        directory_138.id = 138
        directory_138.name = "android_evernote"
        directory_138.parent = directory_2
        directory_138.pootle_path = "/projects/android_evernote/"
        directory_138.obsolete = 0
        directory_138.save()

        directory_4 = Directory()
        directory_4.id = 4
        directory_4.name = "en"
        directory_4.parent = directory_1
        directory_4.pootle_path = "/en/"
        directory_4.obsolete = 1
        directory_4.save()

        language_2 = Language()
        language_2.id = 2
        language_2.code = "en"
        language_2.fullname = "English"
        language_2.specialchars = "“”‘’"
        language_2.nplurals = 2
        language_2.pluralequation = "(n != 1)"
        language_2.directory = directory_4
        language_2.save()

        project_3 = Project()
        project_3.id = 3
        project_3.code = "android_evernote"
        project_3.fullname = "Evernote (Android)"
        project_3.checkstyle = "standard"
        project_3.source_language = language_2
        project_3.directory = directory_138
        project_3.creation_time = None
        project_3.save()

        directory_98 = Directory()
        directory_98.id = 98
        directory_98.name = "ar"
        directory_98.parent = directory_1
        directory_98.pootle_path = "/ar/"
        directory_98.obsolete = 0
        directory_98.save()

        language_91 = Language()
        language_91.id = 91
        language_91.code = "ar"
        language_91.fullname = "Arabic"
        language_91.specialchars = "”“«»"
        language_91.nplurals = 6
        language_91.pluralequation = "n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5"
        language_91.directory = directory_98
        language_91.save()

        directory_8798 = Directory()
        directory_8798.id = 8798
        directory_8798.name = "android_evernote"
        directory_8798.parent = directory_98
        directory_8798.pootle_path = "/ar/android_evernote/"
        directory_8798.obsolete = 0
        directory_8798.save()

        translation_806 = TranslationProject()
        translation_806.id = 806
        translation_806.language = language_91
        translation_806.project = project_3
        translation_806.real_path = "android_evernote/ar"
        translation_806.directory = directory_8798
        translation_806.save()

        store_25642 = Store()
        store_25642.id = 25642
        store_25642.file = "android_evernote/ar/strings.xml.po"
        store_25642.parent = directory_8798
        store_25642.translation_project = translation_806
        store_25642.pootle_path = "/ar/android_evernote/strings.xml.po"
        store_25642.name = "strings.xml.po"
        store_25642.state = 2
        store_25642.creation_time = None
        store_25642.last_sync_revision = "3487500"
        store_25642.obsolete = 0
        store_25642.file_mtime = "162"
        store_25642.save()

        directory_44426 = Directory()
        directory_44426.id = 44426
        directory_44426.name = "release"
        directory_44426.parent = directory_8798
        directory_44426.pootle_path = "/ar/android_evernote/release/"
        directory_44426.obsolete = 0
        directory_44426.save()

        directory_44429 = Directory()
        directory_44429.id = 44429
        directory_44429.name = "7.6"
        directory_44429.parent = directory_44426
        directory_44429.pootle_path = "/ar/android_evernote/release/7.6/"
        directory_44429.obsolete = 0
        directory_44429.save()

        store_131943 = Store()
        store_131943.id = 131943
        store_131943.file = "android_evernote/ar/release/7.6/strings.xml.po"
        store_131943.parent = directory_44429
        store_131943.translation_project = translation_806
        store_131943.pootle_path = "/ar/android_evernote/release/7.6/strings.xml.po"
        store_131943.name = "strings.xml.po"
        store_131943.state = 1
        store_131943.creation_time = "2016-03-04 00:33:02"
        store_131943.last_sync_revision = "1102831"
        store_131943.obsolete = 0
        store_131943.file_mtime = "0"
        store_131943.save()

        unit_5422469 = Unit()
        unit_5422469.id = 5422469
        unit_5422469.store = store_131943
        unit_5422469.index = 0
        unit_5422469.unitid = "Please make sure your internet connection is available."
        unit_5422469.unitid_hash = "005e7826efe6794efc0013e5fe4070d2"
        unit_5422469.source_f = "Please make sure your internet connection is available."
        unit_5422469.source_hash = "005e7826efe6794efc0013e5fe4070d2"
        unit_5422469.source_wordcount = 8
        unit_5422469.source_length = 55
        unit_5422469.target_f = "يرجى التحقق من توفر الاتصال بالإنترنت لديك."
        unit_5422469.target_wordcount = 7
        unit_5422469.target_length = 43
        unit_5422469.developer_comment = "cardscan_internet_issues"
        unit_5422469.translator_comment = None
        unit_5422469.locations = "File: release/7.6/strings.xml ID: bd075daa9136295b6db034fcb0cf75ad"
        unit_5422469.context = None
        unit_5422469.state = -100
        unit_5422469.mtime = "2016-05-07 05:21:48"
        unit_5422469.submitted_by = user_3130
        unit_5422469.submitted_on = "2016-05-07 05:21:48"
        unit_5422469.commented_by = None
        unit_5422469.commented_on = None
        unit_5422469.creation_time = "2016-05-07 05:21:48"
        unit_5422469.revision = 1102831
        unit_5422469.save()

        unit_5125593 = Unit()
        unit_5125593.id = 5125593
        unit_5125593.store = store_25642
        unit_5125593.index = 527
        unit_5125593.unitid = "Cannot share an empty note"
        unit_5125593.unitid_hash = "e06cb66110f368e8e310dab233724617"
        unit_5125593.source_f = "Cannot share an empty note"
        unit_5125593.source_hash = "e06cb66110f368e8e310dab233724617"
        unit_5125593.source_wordcount = 5
        unit_5125593.source_length = 26
        unit_5125593.target_f = "لا يمكن مشاركة مذكرة فارغ"
        unit_5125593.target_wordcount = 26
        unit_5125593.target_length = 5
        unit_5125593.developer_comment = "note_is_empty_share"
        unit_5125593.translator_comment = None
        unit_5125593.state = -100
        unit_5125593.mtime = "2017-07-01 01:41:28 "
        unit_5125593.creation_time = "2015-11-09 15:43:59"
        unit_5422469.revision = 1102831
        unit_5125593.save()

        suggestion_118890 = Suggestion()
        suggestion_118890.id = 118890
        suggestion_118890.target_f = "لا يمكن مشاركة مذكرة فارغ"
        suggestion_118890.target_hash = "1f374f50a66ffe603077a10d715e45d"
        suggestion_118890.unit = unit_5125593
        suggestion_118890.user = user_3130
        suggestion_118890.state = "accepted"
        suggestion_118890.creation_time = "2015-11-09 17:22:01"
        suggestion_118890.review_time = "2015-11-16 08:11:41"
        suggestion_118890.save()

        submission_3043992 = Submission()
        submission_3043992.id = 3043992
        submission_3043992.creation_time = "2015-11-16 08:31:41"
        submission_3043992.translation_project = translation_806
        submission_3043992.submitter = user_3130
        submission_3043992.unit = unit_5125593
        submission_3043992.field = 2
        submission_3043992.type = 3
        submission_3043992.new_value = "لا يمكن مشاركة مذكرة فارغ"
        submission_3043992.store = store_25642
        submission_3043992.suggestion = suggestion_118890
        submission_3043992.save()

        directory_125 = Directory()
        directory_125.id = 125
        directory_125.name = "sr"
        directory_125.parent = directory_1
        directory_125.pootle_path = "/sr/"
        directory_125.obsolete = 0
        directory_125.save()

        language_115 = Language()
        language_115.id = 115
        language_115.code = "sr"
        language_115.fullname = "Serbian"
        language_115.specialchars = "„”’"
        language_115.nplurals = 3
        language_115.pluralequation = "(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)"
        language_115.directory = directory_125
        language_115.save()

        directory_157 = Directory()
        directory_157.id = 157
        directory_157.name = "android_evernote"
        directory_157.parent = directory_125
        directory_157.pootle_path = "/sr/android_evernote/"
        directory_157.obsolete = 0
        directory_157.save()

        translation_25 = TranslationProject()
        translation_25.id = 25
        translation_25.language = language_115
        translation_25.project = project_3
        translation_25.real_path = "android_evernote/sr"
        translation_25.directory = directory_157
        translation_25.pootle_path = "/sr/android_evernote/"
        translation_25.creation_time = None
        translation_25.save()

        # PROJECT 11 DATA
        user_104983 = User()
        user_104983.username = "user104983"
        user_104983.email = "user104983@evernote.cl"
        user_104983.password = "123141241"
        user_104983.full_name = "user104983"
        user_104983.save()

        directory_494 = Directory()
        directory_494.id = 494
        directory_494.name = "web_evernote"
        directory_494.parent = directory_2
        directory_494.pootle_path = "/projects/web_evernote/"
        directory_494.obsolete = 0
        directory_494.save()

        project_11 = Project()
        project_11.id = 11
        project_11.code = "web_evernote"
        project_11.fullname = "Evernote (Web Client)"
        project_11.checkstyle = "standard"
        project_11.source_language = language_2
        project_11.directory = directory_494
        project_11.creation_time = None
        project_11.disabled = 0
        project_11.save()

        directory_70 = Directory()
        directory_70.id = 70
        directory_70.name = "cs"
        directory_70.parent = directory_1
        directory_70.pootle_path = "/cs/"
        directory_70.obsolete = 0
        directory_70.save()

        directory_495 = Directory()
        directory_495.id = 495
        directory_495.name = "web_evernote"
        directory_495.parent = directory_70
        directory_495.pootle_path = "/cs/web_evernote/"
        directory_495.obsolete = 0
        directory_495.save()

        language_63 = Language()
        language_63.id = 63
        language_63.code = "cs"
        language_63.fullname = "Czech"
        language_63.specialchars = "„“‚‘"
        language_63.nplurals = 3
        language_63.pluralequation = "(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2"
        language_63.directory = directory_70
        language_63.save()

        translation_164 = TranslationProject()
        translation_164.id = 164
        translation_164.language = language_63
        translation_164.project = project_11
        translation_164.real_path = "web_evernote_cs"
        translation_164.directory = directory_495
        translation_164.pootle_path = "/cs/web_evernote/"
        translation_164.creation_time = None
        translation_164.save()

        directory_14732 = Directory()
        directory_14732.id = 14732
        directory_14732.name = "resources"
        directory_14732.parent = directory_495
        directory_14732.pootle_path = "/cs/web_evernote/resources/"
        directory_14732.obsolete = 0
        directory_14732.save()

        directory_14733 = Directory()
        directory_14733.id = 14733
        directory_14733.name = "mail"
        directory_14733.parent = directory_14732
        directory_14733.pootle_path = "/cs/web_evernote/resources/mail/"
        directory_14733.obsolete = 0
        directory_14733.save()

        directory_14772 = Directory()
        directory_14772.id = 14722
        directory_14772.name = "premiumcancelation"
        directory_14772.parent = directory_14733
        directory_14772.pootle_path = "/cs/web_evernote/resources/mail/premiumCancelation/"
        directory_14772.obsolete = 0
        directory_14772.save()

        store_38761 = Store()
        store_38761.id = 38761
        store_38761.file = "web_evernote/cs/resources/mail/premiumCancelation/premiumCancelation.xml.master.po"
        store_38761.parent = directory_14772
        store_38761.translation_project = translation_164
        store_38761.pootle_path = "/cs/web_evernote/resources/mail/premiumCancelation/premiumCancelation.xml.master.po"
        store_38761.name = "premiumCancelation.xml.master.po"
        store_38761.state = 2
        store_38761.last_sync_revision = 1503919
        store_38761.obsolete = 0
        store_38761.file_mtime = 1611100759
        store_38761.save()

        unit_1492265 = Unit()
        unit_1492265.id = 1492265
        unit_1492265.store = store_38761
        unit_1492265.index = 12
        unit_1492265.unitid = "- You can no longer allow other users to edit your shared notes"
        unit_1492265.unitid_hash = "60a9e6378b1d19a25b6c2869193b030f"
        unit_1492265.source_f = "- You can no longer allow other users to edit your shared notes"
        unit_1492265.source_hash = "60a9e6378b1d19a25b6c2869193b030f"
        unit_1492265.source_wordcount = 12
        unit_1492265.source_length = 64
        unit_1492265.target_f = "- Nadále nemůžete ostatním uživatelům povolit úpravu vašich sdílených poznámek"
        unit_1492265.target_wordcount = 9
        unit_1492265.target_length = 78
        unit_1492265.developer_comment = "Please wrap the lines so their widths will be under 72 characters"
        unit_1492265.locations = "File: resources/mail/premiumCancelation/premiumCancelation.xml.master ID: 6663f249cc87a375d6f7c839e723cc76"
        unit_1492265.state = -100
        unit_1492265.mtime = "2017-06-24 16:44:27"
        unit_1492265.submitted_by = user_104983
        unit_1492265.submitted_on = "2017-06-24 16:43:56"
        unit_1492265.commented_on = "2013-01-22 08:02:36"
        unit_1492265.commented_by = None
        unit_1492265.revision = 1489088
        unit_1492265.save()

        quality_809005 = QualityCheck()
        quality_809005.id = 809005
        quality_809005.name = "whitespace"
        quality_809005.unit = unit_1492265
        quality_809005.message = "Incorrect whitespace"
        quality_809005.false_positive = 1
        quality_809005.category = 100
        quality_809005.save()

        submission_5089807 = Submission()
        submission_5089807.id = 5089807
        submission_5089807.store = store_38761
        submission_5089807.creation_time = "2017-06-24 16:44:27"
        submission_5089807.translation_project = translation_164
        submission_5089807.submitter = user_104983
        submission_5089807.unit = unit_1492265
        submission_5089807.field = 0
        submission_5089807.type = 6
        submission_5089807.quality_check = quality_809005
        submission_5089807.save()

        # PROJECT WITH ID 4

        directory_162 = Directory()
        directory_162.id = 162
        directory_162.name = "blackberry_evernote"
        directory_162.parent = directory_2
        directory_162.pootle_path = "/projects/blackberry_evernote/"
        directory_162.obsolete = 0
        directory_162.save()

        project_4 = Project()
        project_4.id = 4
        project_4.code = "blackberry_evernote"
        project_4.fullname = "Evernote (BlackBerry)"
        project_4.checkstyle = "standard"
        project_4.source_language = language_2
        project_4.creation_time = None
        project_4.disabled = 1
        project_4.save()

        directory_164 = Directory()
        directory_164.id = 164
        directory_164.name = "blackberry_evernote"
        directory_164.parent = directory_70
        directory_164.pootle_path = "/cs/blackberry_evernote/"
        directory_164.obsolete = 0
        directory_164.save()

        translation_31 = TranslationProject()
        translation_31.id = 31
        translation_31.language = language_63
        translation_31.project = project_4
        translation_31.real_path = "blackberry_evernote/cs"
        translation_31.directory = directory_164
        translation_31.pootle_path = "/cs/blackberry_evernote/"
        translation_31.creation_time = None
        translation_31.save()

        store_84 = Store()
        store_84.id = 84
        store_84.file = "blackberry_evernote/cs/Evernote.rrc.po"
        store_84.parent = directory_164
        store_84.translation_project = translation_31
        store_84.pootle_path = "/cs/blackberry_evernote/Evernote.rrc.po"
        store_84.name = "Evernote.rrc.po"
        store_84.state = 2
        store_84.creation_time = None
        store_84.last_sync_revision = 0
        store_84.obsolete = 0
        store_84.file_mtime = 0
        store_84.save()

        unit_10665 = Unit()
        unit_10665.id = 10665
        unit_10665.store = store_84
        unit_10665.index = 152
        unit_10665.unitid = "No updates are available"
        unit_10665.unitid_hash = "0016d9cdfc10edf7eed97391bdbe4532"
        unit_10665.source_f = "No updates are available"
        unit_10665.source_hash = "0016d9cdfc10edf7eed97391bdbe4532 "
        unit_10665.source_wordcount = 4
        unit_10665.source_length = 24
        unit_10665.target_f = ""
        unit_10665.target_wordcount = 0
        unit_10665.target_length = 0
        unit_10665.developer_comment = "NO_UPDATES_AVAILABLE"
        unit_10665.locations = "File: Evernote.rrc ID: 79d5ea8c5ca650c4dc7ea759b90320d1"
        unit_10665.state = 200
        unit_10665.mtime = "2013-11-27 14:54:36"
        unit_10665.submitted_by = None
        unit_10665.submitted_on = None
        unit_10665.revision = 0
        unit_10665.save()

        print(directory_1.is_clone_of(directory_1))
        cls.data = json.loads(call_command("clone_project", cls.PROJECT_ID))

    def test_cloned_project_should_have_equal_amount_of_translations(self):

        original_project = Project.objects.get(id=self.PROJECT_ID)
        cloned_project_id = self.data['projects'][str(self.PROJECT_ID)]
        cloned_project = Project.objects.get(id=cloned_project_id)

        original_translations = TranslationProject.objects.filter(project_id=original_project.id)
        cloned_translations = TranslationProject.objects.filter(project_id=cloned_project.id)

        original_amounts = original_translations.count()
        cloned_amounts = cloned_translations.count()

        self.assertEquals(original_amounts, cloned_amounts)

    def test_cloned_project_should_have_equal_amount_of_stores(self):

        original_project = Project.objects.get(id=self.PROJECT_ID)
        cloned_project_id = self.data['projects'][str(self.PROJECT_ID)]
        cloned_project = Project.objects.get(id=cloned_project_id)

        original_translations = TranslationProject.objects.filter(project_id=original_project.id)
        cloned_translations = TranslationProject.objects.filter(project_id=cloned_project.id)

        original_stores_amount = 0
        cloned_stores_amount = 0
        for translation in original_translations:
            amount = Store.objects.filter(translation_project_id=translation.id).count()
            original_stores_amount += amount

        for translation in cloned_translations:
            amount = Store.objects.filter(translation_project_id=translation.id).count()
            cloned_stores_amount += amount
        self.assertEquals(original_stores_amount, cloned_stores_amount)

    def test_cloned_project_should_have_equal_amount_of_submissions(self):

        original_project = Project.objects.get(id=self.PROJECT_ID)
        cloned_project_id = self.data['projects'][str(self.PROJECT_ID)]
        cloned_project = Project.objects.get(id=cloned_project_id)

        original_translations = TranslationProject.objects.filter(project_id=original_project.id)
        cloned_translations = TranslationProject.objects.filter(project_id=cloned_project.id)

        original_submission_amount = 0
        cloned_submission_amount = 0
        for translation in original_translations:
            amount = Submission.objects.filter(translation_project_id=translation.id).count()
            original_submission_amount += amount

        for translation in cloned_translations:
            amount = Submission.objects.filter(translation_project_id=translation.id).count()
            cloned_submission_amount += amount

        self.assertEquals(original_submission_amount, cloned_submission_amount)

    def test_cloned_project_should_have_equal_amount_of_units(self):

        original_project = Project.objects.get(id=self.PROJECT_ID)
        cloned_project_id = self.data['projects'][str(self.PROJECT_ID)]
        cloned_project = Project.objects.get(id=cloned_project_id)

        original_translations = TranslationProject.objects.filter(project_id=original_project.id)
        cloned_translations = TranslationProject.objects.filter(project_id=cloned_project.id)

        original_units_amount = 0
        cloned_units_amount = 0
        for translation in original_translations:
            for store in Store.objects.filter(translation_project_id=translation.id):
                amount = Unit.objects.filter(store_id=store.id).count()
                original_units_amount += Unit.objects.filter(store_id=store.id).count()

        for translation in cloned_translations:
            for store in Store.objects.filter(translation_project_id=translation.id):
                amount = Unit.objects.filter(store_id=store.id).count()
                cloned_units_amount += amount
        self.assertEquals(original_units_amount, cloned_units_amount)

    def test_cloned_project_should_have_equal_amount_of_suggestions(self):

        original_project = Project.objects.get(id=self.PROJECT_ID)
        cloned_project_id = self.data['projects'][str(self.PROJECT_ID)]
        cloned_project = Project.objects.get(id=cloned_project_id)

        original_translations = TranslationProject.objects.filter(project_id=original_project.id)
        cloned_translations = TranslationProject.objects.filter(project_id=cloned_project.id)

        original_sugg_amount = 0
        cloned_sugg_amount = 0
        for translation in original_translations:
            for store in Store.objects.filter(translation_project_id=translation.id):
                for unit in Unit.objects.filter(store_id=store.id):
                    amount = Suggestion.objects.filter(unit_id=unit.id).count()
                    original_sugg_amount += amount

        for translation in cloned_translations:
            for store in Store.objects.filter(translation_project_id=translation.id):
                for unit in Unit.objects.filter(store_id=store.id):
                    amount = Suggestion.objects.filter(unit_id=unit.id).count()
                    cloned_sugg_amount += amount
        self.assertEquals(original_sugg_amount, cloned_sugg_amount)

    def test_cloned_project_should_have_equal_amount_of_scorelogs_for_submissions(self):

        submissionsid_to_clone = self.data['submissions']
        for sub_id in submissionsid_to_clone.keys():
            cloned_id = submissionsid_to_clone[sub_id]

            original_scorelogs_amount = ScoreLog.objects.filter(submission_id=sub_id).count()
            cloned_scorelogs_amount = ScoreLog.objects.filter(submission_id=cloned_id).count()

            self.assertEquals(original_scorelogs_amount, cloned_scorelogs_amount)

    def test_cloned_translations_should_have_equal_content(self):
        translations = self.data['translations']
        for translation_id, clone_id in translations.items():
            translation = TranslationProject.objects.get(id=translation_id)
            cloned_translation = TranslationProject.objects.get(id=clone_id)

            self.assertTrue(translation.compare(cloned_translation))

    def test_cloned_stores_should_have_equal_content(self):
        stores = self.data['stores']
        for store_id, clone_id in stores.items():
            store = Store.objects.get(id=store_id)
            cloned_store = Store.objects.get(id=clone_id)

            self.assertTrue(store.compare(cloned_store))

    def test_cloned_units_should_have_equal_content(self):
        units = self.data['units']
        for unit_id, clone_id in units.items():
            unit = Unit.objects.get(id=unit_id)
            clone_unit = Unit.objects.get(id=clone_id)

            self.assertTrue(unit.compare(clone_unit))

    def test_scorelogs_should_have_equal_content(self):
        submissions = self.data['submissions']
        for submission_id, clone_id in submissions.items():
            submission = Submission.objects.get(id=submission_id)
            clone_submission = Submission.objects.get(id=clone_id)
            print("\nOriginal scorelogs:")

            for scorelog in ScoreLog.objects.filter(submission_id=submission.id):

                for key, value in model_to_dict(scorelog).items():
                    print(f"{key} => {value}")
                print()
            print("\nCloned scorelogs:")

            for scorelog in ScoreLog.objects.filter(submission_id=clone_submission):
                for key, value in model_to_dict(scorelog).items():
                    print(f"{key} => {value}")
                print()
            print(self.RECORD_SEPARATOR)

    def test_suggestions_should_have_equal_content(self):
        suggestions = self.data['suggestions']
        for suggestion_id, clone_id in suggestions.items():
            suggestion = Suggestion.objects.get(id=suggestion_id)
            clone = Suggestion.objects.get(id=clone_id)

            self.assertTrue(suggestion.compare(clone))

    def test_submissions_should_have_equal_content(self):
        submissions = self.data['submissions']
        for submission_id, clone_id in submissions.items():
            submission = Submission.objects.get(id=submission_id)
            clone = Submission.objects.get(id=clone_id)

            self.assertTrue(submission.compare(clone))
