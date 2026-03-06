/**
 * Sync martor ACE editor with localized field tabs/dropdowns.
 *
 * A single main martor editor is rendered per field. The per-language panels
 * are kept hidden (display:none) — they only hold textareas as data stores.
 * When the user switches language, the ACE editor content is swapped to match
 * the selected panel's textarea. When the user edits in ACE, the value is
 * written back to the active panel's textarea.
 */
(function($) {
    'use strict';

    if (typeof ace === 'undefined') return;

    /**
     * Find the currently-active panel's lang code for a widget.
     */
    function getActiveLangCode($widget) {
        var display = $widget.data('display');
        if (display === 'dropdown') {
            return $widget.find('.i18n-fields-language-selector').val();
        }
        // tabs: read from the active tab's label "for" attr → panel id ends with _langcode
        var $activeLabel = $widget.find('li.i18n-fields-widget.tab.active label');
        if ($activeLabel.length) {
            var panelId = $activeLabel.attr('for');
            var $panel = $('#' + panelId);
            return $panel.data('lang');
        }
        // fallback: first panel
        var $first = $widget.find('.i18n-fields-panel').first();
        return $first.data('lang');
    }

    /**
     * Get the active panel by lang code.
     */
    function getActivePanel($widget) {
        var langCode = getActiveLangCode($widget);
        return $widget.find('.i18n-fields-panel[data-lang="' + langCode + '"]');
    }

    /**
     * Load the active panel's textarea value into the ACE editor.
     */
    function syncMartorWithActivePanel($widget) {
        $widget.find('.main-martor').each(function() {
            var $martor = $(this);
            var fieldName = $martor.data('field-name');
            var editorId = 'martor-' + fieldName;

            try {
                var editor = ace.edit(editorId);
                var $panel = getActivePanel($widget);
                var currentTextVal = $panel.find('textarea').val() || '';
                editor.setValue(currentTextVal);
                editor.clearSelection();
            } catch (e) {
                // Editor not ready yet
            }
        });
    }

    // Expose function globally so it can be called from i18n-fields-admin.js
    window.syncMartorWithActivePanel = syncMartorWithActivePanel;

    $(window).on('load', function() {
        // Setup ACE -> textarea sync (write-back on user edits)
        $('.i18n-fields-widget').each(function() {
            var $widget = $(this);

            $widget.find('.main-martor').each(function() {
                var $martor = $(this);
                var fieldName = $martor.data('field-name');
                var editorId = 'martor-' + fieldName;

                try {
                    var editor = ace.edit(editorId);
                    editor.on('change', function() {
                        // Only sync on real user edits, not programmatic setValue
                        if (editor.curOp && editor.curOp.command.name) {
                            var value = editor.getValue();
                            var $panel = getActivePanel($widget);
                            $panel.find('textarea').val(value);
                        }
                    });
                } catch (e) {
                    // Editor not ready yet
                }
            });
        });

        // Sync ACE editor when language tab is clicked
        $(document).on('click', 'li.i18n-fields-widget.tab label', function() {
            var $widget = $(this).closest('.i18n-fields-widget[data-display]');
            // Small delay so the active tab class is updated first
            setTimeout(function() { syncMartorWithActivePanel($widget); }, 50);
        });

        // Sync ACE editor when language dropdown changes
        $(document).on('change', '.i18n-fields-language-selector', function() {
            var $widget = $(this).closest('.i18n-fields-widget[data-display]');
            setTimeout(function() { syncMartorWithActivePanel($widget); }, 50);
        });

        // Initial sync for all widgets
        $('.i18n-fields-widget[data-display]').each(function() {
            syncMartorWithActivePanel($(this));
        });
    });

})(django.jQuery);
