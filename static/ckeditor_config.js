CKEDITOR.plugins.addExternal( 'youtube', '/static/ckeditor/ckeditor/plugins/youtube/', 'plugin.js' );
CKEDITOR.editorConfig = function (config) {
    config.extraPlugins = 'youtube';
};
