#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pinyin.dictionaryonline
import pinyin.dictionary
from pinyin.logger import log
import pinyin.updater

import hooks
import mediamanager
import notifier
import utils

import statsandgraphs
import shortcutkeys


class PinyinToolkit(object):
    def __init__(self, mw, config):
        log.info("Pinyin Toolkit is initializing")
        
        # Test internet connectivity by performing a gTrans call.
        # If this call fails then translations are disabled until Anki is restarted.
        # This prevents a several second delay from occuring when changing a field with no internet
        if (config.fallbackongoogletranslate):
            config.fallbackongoogletranslate = pinyin.dictionaryonline.gCheck(config.dictlanguage)
            log.info("Google Translate has tested internet access and reports status %s", config.fallbackongoogletranslate)
        
        # Store the configuration and mw
        self.mw = mw
        self.config = config
        
        # Build objects we use to interface with Anki
        self.notifier = notifier.AnkiNotifier()
        self.mediamanager = mediamanager.AnkiMediaManager(self.mw)
        
        # Build the updater
        dictionary = pinyin.dictionary.PinyinDictionary.load(config.dictlanguage, needmeanings=config.needmeanings)
        self.updater = pinyin.updater.FieldUpdater(self.notifier, self.mediamanager, self.config, dictionary)
        
        # Finally, build the hooks.  Make sure you store a reference to these, because otherwise they
        # get garbage collected, causing garbage collection of the actions they contain
        self.hooks = [hookbuilder(self.mw, self.notifier, self.mediamanager, self.config, self.updater) for hookbuilder in [hooks.FocusHook, hooks.SampleSoundsHook, hooks.MissingInformationHook]]
    
    def installhooks(self):
        # Install all hooks
        for hook in self.hooks:
            hook.install()
    
        # Tell Anki about the plugin
        self.mw.registerPlugin("Mandarin Chinese Pinyin Toolkit", 4)
