// The Firefox rule against unescaped HTML (spec seguranca-doacoes, section 8): no-unsanitized/method and /property as errors,
// with esc() as the escape. What existed on 2026-11-03 sits in eslint-suppressions.json, a list that only shrinks.
import nounsanitized from 'eslint-plugin-no-unsanitized';

const rules = {
  'no-unsanitized/method': ['error', { escape: { methods: ['esc'] } }],
  'no-unsanitized/property': ['error', { escape: { methods: ['esc'] } }],
};
export default [
  // outside code, and the data files (a value assigned to window, no code; the poisoned-data probe covers what they carry)
  { ignores: ['docs/superpowers/previews/assets/vendor/**', 'docs/superpowers/previews/assets/bi-data.js', 'docs/superpowers/previews/assets/bi-geo*.js',
    'docs/superpowers/previews/assets/bi-federal.js', 'docs/superpowers/previews/assets/bi-ledger-interest.js',
    'docs/superpowers/previews/assets/dinheiro-r1-data.js', 'docs/superpowers/previews/assets/tres-poderes*-data.js'] },
  { files: ['docs/superpowers/previews/assets/*.js'], plugins: { 'no-unsanitized': nounsanitized }, rules,
    languageOptions: { ecmaVersion: 'latest', sourceType: 'script' } },
  // modules: the home module and the two sources build-simulation.py puts into it
  { files: ['docs/superpowers/previews/assets/home-map.js', 'docs/superpowers/previews/assets/hero3d.js', 'docs/superpowers/previews/assets/modals.js'], languageOptions: { sourceType: 'module' } },
];
