/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t } from 'utils/i18n';

import { greetings } from '../greetings';
import RandomMessage from './RandomMessage';
import RandomSymbolsBackground from './RandomSymbolsBackground';


const Hero = () => (
  <div>
    <div className="hero-background">
      <RandomSymbolsBackground />
    </div>
    <div className="hero-background-overlay">
      <h1><RandomMessage items={greetings} /></h1>
      <h2>{t('Join our translation community')}</h2>
    </div>
  </div>
);


export default Hero;
