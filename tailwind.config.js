/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    darkMode: 'media',
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'

        './node_modules/flowbite/**/*.js'
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    "50": "#f0fdfa",
                    "100": "#ccfbf1",
                    "200": "#99f6e4",
                    "300": "#5eead4",
                    "400": "#2dd4bf",
                    "500": "#14b8a6",
                    "600": "#0d9488",
                    "700": "#0f766e",
                    "800": "#115e59",
                    "900": "#134e4a",
                    "950": "#042f2e"
                },
                'light-bg-primary': '#f5f5f5',
                'dark-bg-primary': '#121826',
                'light-bg-secondary': '#ffffff',
                'dark-bg-secondary': '#181f39',

                'light-text-primary': '#394150',
                'dark-text-primary': '#d2d5da',
                'light-text-secondary': '#394150',
                'dark-text-secondary': '#97A3B6',

                'light-border-primary': '#cdcfd1',
                'dark-border-primary': '#4a5568',

            },
            fontFamily: {
                'body': [
                    'Inter',
                    'ui-sans-serif',
                    'system-ui',
                    '-apple-system',
                    'system-ui',
                    'Segoe UI',
                    'Roboto',
                    'Helvetica Neue',
                    'Arial',
                    'Noto Sans',
                    'sans-serif',
                    'Apple Color Emoji',
                    'Segoe UI Emoji',
                    'Segoe UI Symbol',
                    'Noto Color Emoji'
                ],
                'sans': [
                    'Inter',
                    'ui-sans-serif',
                    'system-ui',
                    '-apple-system',
                    'system-ui',
                    'Segoe UI',
                    'Roboto',
                    'Helvetica Neue',
                    'Arial',
                    'Noto Sans',
                    'sans-serif',
                    'Apple Color Emoji',
                    'Segoe UI Emoji',
                    'Segoe UI Symbol',
                    'Noto Color Emoji'
                ]
            },
            typography: ({theme}) => ({
                orange: {
                    css: {
                        '--tw-format-body': theme('colors.orange[500]'),
                        '--tw-format-headings': theme('colors.orange[900]'),
                        '--tw-format-lead': theme('colors.orange[500]'),
                        '--tw-format-links': theme('colors.orange[600]'),
                        '--tw-format-bold': theme('colors.orange[900]'),
                        '--tw-format-counters': theme('colors.orange[500]'),
                        '--tw-format-bullets': theme('colors.orange[500]'),
                        '--tw-format-hr': theme('colors.orange[200]'),
                        '--tw-format-quotes': theme('colors.orange[900]'),
                        '--tw-format-quote-borders': theme('colors.orange[300]'),
                        '--tw-format-captions': theme('colors.orange[700]'),
                        '--tw-format-code': theme('colors.orange[900]'),
                        '--tw-format-code-bg': theme('colors.orange[50]'),
                        '--tw-format-pre-code': theme('colors.orange[100]'),
                        '--tw-format-pre-bg': theme('colors.orange[900]'),
                        '--tw-format-th-borders': theme('colors.orange[300]'),
                        '--tw-format-td-borders': theme('colors.orange[200]'),
                        '--tw-format-th-bg': theme('colors.orange[50]'),
                        '--tw-format-invert-body': theme('colors.orange[200]'),
                        '--tw-format-invert-headings': theme('colors.white'),
                        '--tw-format-invert-lead': theme('colors.orange[300]'),
                        '--tw-format-invert-links': theme('colors.white'),
                        '--tw-format-invert-bold': theme('colors.white'),
                        '--tw-format-invert-counters': theme('colors.orange[400]'),
                        '--tw-format-invert-bullets': theme('colors.orange[600]'),
                        '--tw-format-invert-hr': theme('colors.orange[700]'),
                        '--tw-format-invert-quotes': theme('colors.pink[100]'),
                        '--tw-format-invert-quote-borders': theme('colors.orange[700]'),
                        '--tw-format-invert-captions': theme('colors.orange[400]'),
                        '--tw-format-invert-code': theme('colors.white'),
                        '--tw-format-invert-pre-code': theme('colors.orange[300]'),
                        '--tw-format-invert-pre-bg': 'rgb(0 0 0 / 50%)',
                        '--tw-format-invert-th-borders': theme('colors.orange[600]'),
                        '--tw-format-invert-td-borders': theme('colors.orange[700]'),
                        '--tw-format-invert-th-bg': theme('colors.orange[700]'),
                    },
                },
            }),
        },
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('flowbite/plugin'),
        require('flowbite-typography'),
    ],
};
