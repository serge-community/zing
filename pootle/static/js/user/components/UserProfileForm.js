/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import assign from 'object-assign';
import React from 'react';
import _ from 'underscore';

import UserAPI from 'api/UserAPI';

import Avatar from 'components/Avatar';
import FormElement from 'components/FormElement';


export const UserProfileForm = React.createClass({

  propTypes: {
    onSuccess: React.PropTypes.func.isRequired,
    user: React.PropTypes.object.isRequired,
  },

  getInitialState() {
    const formData = _.pick(
      this.props.user,
      'full_name', 'twitter', 'linkedin', 'website', 'bio'
    );
    return {
      formData,
      errors: {},
    };
  },

  handleChange(name, value) {
    this.setState((prevState, props) => {
      const newData = assign({}, prevState.formData);
      newData[name] = value;
      const isDirty = !_.isEqual(newData, props.user);

      return {
        isDirty,
        formData: newData,
      };
    });
  },

  handleSubmit(e) {
    e.preventDefault();
    UserAPI.update(this.props.user.id, this.state.formData)
      .then(
        () => {
          this.props.onSuccess();
        },
        (data) => {
          this.setState(() => ({
            errors: data.responseJSON.errors,
          }));
        }
      );
  },


  /* Layout */

  render() {
    const { user } = this.props;
    const { errors } = this.state;
    const { formData } = this.state;
    const avatarHelpMsg = gettext(
      'To set or change your avatar image for your email address ' +
      '(%(email)s), please go to gravatar.com.'
    );
    const avatarHelp = interpolate(avatarHelpMsg, { email: user.email }, true);

    return (
      <form
        method="post"
        id="item-form"
        autoComplete="off"
        onSubmit={this.handleSubmit}
      >
        <div className="fields">
          <FormElement
            label={gettext('Full Name')}
            placeholder={gettext('Your Full Name')}
            autoFocus
            handleChange={this.handleChange}
            name="full_name"
            errors={errors.full_name}
            value={formData.full_name}
          />
          <p>
            <label>{gettext('Avatar')}</label>
            <Avatar
              email={user.email_md5}
              displayName={formData.full_name}
              size={48}
              username={user.username}
            />
            <span className="helptext">{avatarHelp}</span>
          </p>
          <p className="divider" />
          <FormElement
            label={gettext('Twitter')}
            handleChange={this.handleChange}
            placeholder={gettext('Your Twitter username')}
            maxLength="15"
            name="twitter"
            errors={errors.twitter}
            value={formData.twitter}
          />
          <FormElement
            label={gettext('LinkedIn')}
            handleChange={this.handleChange}
            placeholder={gettext('Your LinkedIn profile URL')}
            name="linkedin"
            errors={errors.linkedin}
            value={formData.linkedin}
          />
          <FormElement
            label={gettext('Website')}
            handleChange={this.handleChange}
            placeholder={gettext('Your Personal website/blog URL')}
            name="website"
            errors={errors.website}
            value={formData.website}
          />
          <FormElement
            type="textarea"
            label={gettext('Short Bio')}
            handleChange={this.handleChange}
            placeholder={gettext('Why are you part of our translation project? ' +
                                 'Describe yourself, inspire others!')}
            name="bio"
            errors={errors.bio}
            value={formData.bio}
          />
        </div>
        <p className="buttons">
          <input
            type="submit"
            className="btn btn-primary"
            disabled={!this.state.isDirty}
            value={gettext('Save')}
          />
        </p>
      </form>
    );
  },

});


export default UserProfileForm;
