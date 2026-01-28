(function($) {
    'use strict';

    // Storage key for remembering selected language
    var STORAGE_KEY = 'i18n-fields-lang';

    /**
     * Sync all tab-based widgets to show the specified language
     */
    function syncTabs(lang) {
        $('.i18n-fields-widget[data-display="tabs"]').each(function() {
            var $widget = $(this);
            var $tabs = $widget.find('li.i18n-fields-widget.tab');

            $tabs.each(function() {
                var $tab = $(this);
                var $label = $tab.find('label');
                var labelText = $label.text().toLowerCase().trim();

                if (labelText === lang.toLowerCase()) {
                    // Update active tab
                    $tabs.removeClass('active');
                    $tab.addClass('active');

                    // Show corresponding panel
                    var panelId = $label.attr('for');
                    $widget.find('.i18n-fields-panel').removeClass('active').hide();
                    $('#' + panelId).addClass('active').show();

                    // Trigger resize for editors
                    triggerEditorResize($('#' + panelId));
                }
            });
        });
    }

    /**
     * Sync all dropdown-based widgets to show the specified language
     */
    function syncDropdowns(lang) {
        $('.i18n-fields-widget[data-display="dropdown"]').each(function() {
            var $widget = $(this);
            var $selector = $widget.find('.i18n-fields-language-selector');

            // Find option by text (language name)
            $selector.find('option').each(function() {
                if ($(this).text().toLowerCase().trim() === lang.toLowerCase()) {
                    $selector.val($(this).val());
                }
            });

            // Show corresponding panel by language code
            var selectedLang = $selector.val();
            $widget.find('.i18n-fields-panel').removeClass('active').hide();
            $widget.find('.i18n-fields-panel[data-lang="' + selectedLang + '"]')
                .addClass('active').show();

            // Trigger resize for editors
            triggerEditorResize($widget.find('.i18n-fields-panel.active'));
        });
    }

    /**
     * Sync readonly tab-based widgets to show the specified language
     */
    function syncReadonlyTabs(langCode) {
        $('.i18n-readonly-widget.i18n-tab-mode').each(function() {
            var $widget = $(this);

            // Update active tab
            $widget.find('.i18n-readonly-tab').removeClass('active');
            $widget.find('.i18n-readonly-tab[data-lang="' + langCode + '"]').addClass('active');

            // Show corresponding content
            $widget.find('.i18n-readonly-content').hide().removeClass('active');
            $widget.find('.i18n-readonly-content[data-lang="' + langCode + '"]').show().addClass('active');
        });
    }

    /**
     * Sync readonly dropdown-based widgets to show the specified language
     */
    function syncReadonlyDropdowns(langCode) {
        $('.i18n-readonly-widget.i18n-dropdown-mode').each(function() {
            var $widget = $(this);
            var $select = $widget.find('.i18n-readonly-select');

            // Set dropdown value
            $select.val(langCode);

            // Show corresponding content
            $widget.find('.i18n-readonly-content').hide().removeClass('active');
            $widget.find('.i18n-readonly-content[data-lang="' + langCode + '"]').show().addClass('active');
        });
    }

    /**
     * Sync all widgets (both tabs and dropdowns, editable and readonly) to the same language
     */
    function syncAllWidgets(lang) {
        syncTabs(lang);
        syncDropdowns(lang);

        // For readonly widgets, we need the language code, not the name
        // Try to find the code by looking at existing widgets
        var langCode = findLangCodeByName(lang);
        if (langCode) {
            syncReadonlyTabs(langCode);
            syncReadonlyDropdowns(langCode);
        }

        // Store preference
        if (window.sessionStorage) {
            try {
                window.sessionStorage.setItem(STORAGE_KEY, lang);
            } catch (e) {
                // Storage might be full or disabled
            }
        }
    }

    /**
     * Find language code by language name
     */
    function findLangCodeByName(langName) {
        var langCode = null;
        // Check editable dropdown widgets for the mapping
        $('.i18n-fields-widget[data-display="dropdown"] .i18n-fields-language-selector option').each(function() {
            if ($(this).text().toLowerCase().trim() === langName.toLowerCase()) {
                langCode = $(this).val();
                return false; // break
            }
        });
        // Also check readonly dropdown widgets
        if (!langCode) {
            $('.i18n-readonly-widget .i18n-readonly-select option').each(function() {
                if ($(this).text().toLowerCase().trim() === langName.toLowerCase()) {
                    langCode = $(this).val();
                    return false; // break
                }
            });
        }
        // Check readonly tab widgets
        if (!langCode) {
            $('.i18n-readonly-widget .i18n-readonly-tab').each(function() {
                if ($(this).text().toLowerCase().trim() === langName.toLowerCase()) {
                    langCode = $(this).data('lang');
                    return false; // break
                }
            });
        }
        return langCode;
    }

    /**
     * Trigger resize events for editors that need it (Martor, ACE, CodeMirror)
     */
    function triggerEditorResize($panel) {
        if (!$panel || !$panel.length) return;

        // Martor/ACE editor resize
        $panel.find('.ace_editor').each(function() {
            if (typeof ace !== 'undefined') {
                var editor = ace.edit(this);
                if (editor) {
                    setTimeout(function() {
                        editor.resize();
                    }, 10);
                }
            }
        });

        // CodeMirror resize
        $panel.find('.CodeMirror').each(function() {
            if (this.CodeMirror) {
                this.CodeMirror.refresh();
            }
        });

        // Generic resize event
        $(window).trigger('resize');
    }

    /**
     * Initialize tab-based widgets
     */
    function initTabs() {
        $('.i18n-fields-widget[data-display="tabs"]').each(function() {
            var $widget = $(this);

            // Skip if already initialized
            if ($widget.data('i18n-initialized')) return;
            $widget.data('i18n-initialized', true);

            // Hide all panels initially
            $widget.find('.i18n-fields-panel').hide();

            // Find and activate first tab
            var $firstTab = $widget.find('li.i18n-fields-widget.tab').first();
            var $firstLabel = $firstTab.find('label');
            var firstPanelId = $firstLabel.attr('for');

            $firstTab.addClass('active');
            $('#' + firstPanelId).addClass('active').show();
        });

        // Tab click handler (using delegation for dynamically added content)
        $(document).off('click.i18nfields', 'li.i18n-fields-widget.tab label');
        $(document).on('click.i18nfields', 'li.i18n-fields-widget.tab label', function(e) {
            e.preventDefault();
            var lang = $(this).text().trim();
            syncAllWidgets(lang);
            return false;
        });
    }

    /**
     * Initialize dropdown-based widgets
     */
    function initDropdowns() {
        $('.i18n-fields-widget[data-display="dropdown"]').each(function() {
            var $widget = $(this);

            // Skip if already initialized
            if ($widget.data('i18n-initialized')) return;
            $widget.data('i18n-initialized', true);

            // Hide all panels initially
            $widget.find('.i18n-fields-panel').hide();

            // Get first language and show its panel
            var $selector = $widget.find('.i18n-fields-language-selector');
            var firstLang = $selector.find('option').first().val();

            $widget.find('.i18n-fields-panel[data-lang="' + firstLang + '"]')
                .addClass('active').show();
        });

        // Dropdown change handler (using delegation)
        $(document).off('change.i18nfields', '.i18n-fields-language-selector');
        $(document).on('change.i18nfields', '.i18n-fields-language-selector', function() {
            var lang = $(this).find('option:selected').text().trim();
            syncAllWidgets(lang);
        });
    }

    /**
     * Restore previously selected language from storage
     */
    function restoreLanguagePreference() {
        if (window.sessionStorage) {
            try {
                var lang = window.sessionStorage.getItem(STORAGE_KEY);
                if (lang) {
                    syncAllWidgets(lang);
                }
            } catch (e) {
                // Storage might be disabled
            }
        }
    }

    /**
     * Main initialization function
     */
    function init() {
        initTabs();
        initDropdowns();
        restoreLanguagePreference();
    }

    /**
     * Initialize on document ready
     */
    $(function() {
        init();

        // Listen for sync events from readonly widgets
        $(document).on('i18n-fields-sync', function(e, lang) {
            syncAllWidgets(lang);
        });
    });

    /**
     * Re-initialize on page load (for dynamically added content)
     */
    $(window).on('load', function() {
        init();
    });

    /**
     * Handle Django admin inline additions
     */
    $(document).on('formset:added', function(event, $row, formsetName) {
        // Reset initialized flag for new widgets
        $row.find('.i18n-fields-widget[data-display]').data('i18n-initialized', false);

        // Re-initialize
        init();
    });

})(django.jQuery);

/**
 * Global functions for readonly i18n widgets (called from inline onclick/onchange)
 */
function i18nReadonlyTabClick(btn) {
    var $btn = django.jQuery(btn);
    var lang = $btn.text().trim();

    // Use the internal sync function to sync all widgets
    // We need to access the module's syncAllWidgets, but since it's in an IIFE,
    // we'll dispatch a custom event that the module can listen to
    django.jQuery(document).trigger('i18n-fields-sync', [lang]);
}

function i18nReadonlySwitch(select) {
    var $select = django.jQuery(select);
    var lang = $select.find('option:selected').text().trim();

    // Use the internal sync function via custom event
    django.jQuery(document).trigger('i18n-fields-sync', [lang]);
}
