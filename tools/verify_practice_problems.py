"""Run introductory reference programs and starters through every installed runner."""
from practice_problem_content import SPECS
from verify_hard_problems import main
from verify_problem import verify

if __name__ == '__main__':
    for slug in SPECS:
        verify(slug)
    main(tuple(SPECS), 'practice-results.json')
