import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'quality_eval', ROOT / '.agents/scripts/evaluate_skill_quality.py'
)
quality = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality)


class CreativeQualityEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases = {'cases': [{'id': 'portrait', 'prompt': 'Preserve identity.',
                                'criteria': {'fidelity': 'Keep approved appearance.'}}]}
        self.before = {'outputs': {'portrait': 'Keep face; add freckles.'}}
        self.after = {'outputs': {'portrait': 'Keep face and skin markings.'}}
        self.pack, self.key = quality.blind_pairs(self.cases, self.before, self.after, 7)
        self.judgments = {'pack_sha256': quality.digest(self.pack), 'cases': [{'id': 'portrait', 'ratings': {
            label: {'criteria': {'fidelity': {'score': 2, 'evidence': 'Appearance is explicitly retained.'}},
                    'hard_failures': []} for label in ('A', 'B')
        }}]}

    def test_blinding_preserves_complete_outputs_without_version_labels(self):
        case = self.pack['cases'][0]
        self.assertEqual(set(case['candidates']), {'A', 'B'})
        self.assertEqual(set(case['candidates'].values()),
                         {self.before['outputs']['portrait'], self.after['outputs']['portrait']})
        self.assertNotIn('before', str(self.pack))
        self.assertEqual((self.pack, self.key), quality.blind_pairs(self.cases, self.before, self.after, 7))

    def test_incomplete_or_duplicate_cases_are_rejected(self):
        with self.assertRaises(ValueError):
            quality.blind_pairs(self.cases, {'outputs': {}}, self.after, 7)
        self.cases['cases'].append(self.cases['cases'][0])
        with self.assertRaises(ValueError):
            quality.blind_pairs(self.cases, self.before, self.after, 7)

    def test_ties_are_retained_and_hard_failure_overrides_score(self):
        result = quality.summarize(self.pack, self.key, self.judgments)
        self.assertEqual(result['counts']['tie'], 1)
        self.judgments['cases'][0]['ratings']['A']['hard_failures'] = ['Adds freckles contrary to the explicit lock.']
        result = quality.summarize(self.pack, self.key, self.judgments)
        self.assertEqual(result['cases'][0]['winner'], self.key['cases']['portrait']['B'])
        self.judgments['cases'][0]['ratings']['B']['hard_failures'] = ['Also changes locked identity.']
        self.assertEqual(quality.summarize(self.pack, self.key, self.judgments)['counts']['neither'], 1)

    def test_missing_evidence_out_of_range_and_boolean_scores_fail(self):
        rating = self.judgments['cases'][0]['ratings']['A']['criteria']['fidelity']
        for score in [True, -1, 4, 2.5]:
            rating['score'] = score
            with self.assertRaises(ValueError):
                quality.summarize(self.pack, self.key, self.judgments)
        rating['score'] = 2
        rating['evidence'] = ' '
        with self.assertRaises(ValueError):
            quality.summarize(self.pack, self.key, self.judgments)

    def test_missing_case_or_criterion_is_not_silently_scored(self):
        missing = {'pack_sha256': quality.digest(self.pack), 'cases': []}
        with self.assertRaises(ValueError):
            quality.summarize(self.pack, self.key, missing)
        self.judgments['cases'][0]['ratings']['B']['criteria'] = {}
        with self.assertRaises(ValueError):
            quality.summarize(self.pack, self.key, self.judgments)

    def test_changed_pack_or_invalid_key_is_rejected(self):
        self.pack['cases'][0]['candidates']['A'] += ' Changed after judging.'
        with self.assertRaises(ValueError):
            quality.summarize(self.pack, self.key, self.judgments)

    def test_ad_development_cases_can_be_blinded_without_losing_the_brief(self):
        scenarios = json.loads(
            (ROOT / 'tests/fixtures/ad_development_cases.json').read_text()
        )
        before = {'outputs': {case['id']: 'Synthetic baseline output.'
                              for case in scenarios['cases']}}
        after = {'outputs': {case['id']: 'Synthetic revised output.'
                             for case in scenarios['cases']}}
        pack, key = quality.blind_pairs(scenarios, before, after, 17)
        self.assertEqual(key['pack_sha256'], quality.digest(pack))
        self.assertEqual(len(pack['cases']), len(scenarios['cases']))
        for original, blinded in zip(scenarios['cases'], pack['cases'], strict=True):
            with self.subTest(case=original['id']):
                self.assertEqual(blinded['prompt'], original['prompt'])
                self.assertEqual(blinded['criteria'], original['criteria'])
                self.assertEqual(set(blinded['candidates'].values()),
                                 {'Synthetic baseline output.', 'Synthetic revised output.'})
                self.assertTrue(
                    (ROOT / '.agents/skills' / original['skill'] / 'SKILL.md').is_file()
                )

    def test_ad_development_suite_covers_every_requested_format_and_regression(self):
        scenarios = json.loads(
            (ROOT / 'tests/fixtures/ad_development_cases.json').read_text()
        )
        indexed = quality.indexed_cases(scenarios)
        formats = {'seedance-ugc-ads', 'seedance-product-demo-ads',
                   'seedance-story-ads', 'ad-motion-graphics',
                   'seedance-testimonial-ads', 'seedance-musical-ads',
                   'seedance-match-cut-ads', 'seedance-fashion-ads',
                   'seedance-pov-ads', 'seedance-deadpan-ads',
                   'seedance-handcrafted-ads', 'seedance-practical-illusion-ads'}
        self.assertTrue(formats <= {case['skill'] for case in indexed.values()})
        self.assertTrue({'quiet_but_compelling', 'one_source_native_cuts',
                         'batch_repetition', 'technical_camouflage',
                         'missing_evidence', 'narrow_revision'} <= set(indexed))
        self.assertEqual(scenarios['scope'], 'offline_prompt_quality')


if __name__ == '__main__':
    unittest.main()
