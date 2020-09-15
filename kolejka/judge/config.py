# vim:ts=4:sts=4:sw=4:expandtab


import sys
assert sys.version_info >= (3, 6)


DISTRIBUTION_PATH = 'kolejka-judge'
DISTRIBUTION_ADDRESS = 'https://kolejka.matinf.uj.edu.pl/' + DISTRIBUTION_PATH

SATORI_STRING_LENGTH = 4096
SATORI_RESULT = 'satori'

LOG = 'log'
COLLECTED_LOG = 'log.zip'

SOLUTION = 'solution'
SOLUTION_SOURCE = SOLUTION + '/src'
SOLUTION_BUILD = SOLUTION + '/build'
SOLUTION_EXEC = SOLUTION + '/exec'

TOOL = 'tools'
TOOL_SOURCE = TOOL + '/src/{tool_name}'
TOOL_BUILD = TOOL + '/build/{tool_name}'
TOOL_EXEC = TOOL + '/{tool_name}'

TEST = 'test'
TEST_INPUT = TEST + '/input'
TEST_HINT = TEST + '/hint'
TEST_ANSWER = TEST + '/answer'

MULTITEST = TEST + '/tests'
MULTITEST_INPUT_GLOB = '**/*.in'
MULTITEST_INPUT_NAME = (r'^.*/(.*)[.]in$', r'\1')
MULTITEST_INPUT_HINT = (r'^(.*)[.]in$', r'\1.out')
MULTITEST_INPUT_CORES = (r'^(.*)[.]in$', r'\1.cores')
MULTITEST_INPUT_TIME = (r'^(.*)[.]in$', r'\1.time')
MULTITEST_INPUT_CPU_TIME = (r'^(.*)[.]in$', r'\1.cpu_time')
MULTITEST_INPUT_REAL_TIME = (r'^(.*)[.]in$', r'\1.real_time')
MULTITEST_INPUT_MEMORY = (r'^(.*)[.]in$', r'\1.mem')
MULTITEST_INPUT_SCORE = (r'^(.*)[.]in$', r'\1.score')

MULTITEST_SINGLE = TEST + '/multi/{test_name}'
MULTITEST_INPUT = MULTITEST_SINGLE + '/input'
MULTITEST_HINT = MULTITEST_SINGLE + '/hint'
MULTITEST_ANSWER = MULTITEST_SINGLE + '/answer'

GROUP_ALL  = 'kolejkajudgerun'

USER_TEST = 'kolejkajudgetest'
USER_BUILD = 'kolejkajudgebuild'
USER_EXEC = 'kolejkajudgeexec'

SYSTEM_GROUPS = [
    GROUP_ALL,
]
SYSTEM_USERS = [
    {
        'user_name' : USER_TEST,
        'home' : 'home_'+USER_TEST,
        'groups' : [ GROUP_ALL, ],
    } , {
        'user_name' : USER_BUILD,
        'home' : 'home_'+USER_BUILD,
        'groups' : [ GROUP_ALL, ],
    } , {
        'user_name' : USER_EXEC,
        'home' : 'home_'+USER_EXEC,
        'groups' : [ GROUP_ALL, ],
    }
]
SYSTEM_DIRECTORIES = [
    {
        'path' : '.',
        'user_name' : USER_TEST,
        'group_name' : GROUP_ALL,
        'mode' : 0o2750,
    } , {
        'path' : LOG,
        'mode' : 0o2700,
    } , {
        'path' : TEST,
        'user_name' : USER_TEST,
        'group_name' : USER_TEST,
        'mode' : 0o2750,
    } , {
        'path' : SOLUTION,
        'user_name' : USER_TEST,
        'group_name' : GROUP_ALL,
        'mode' : 0o2750,
    } , {
        'path' : SOLUTION_SOURCE,
        'user_name' : USER_TEST,
        'group_name' : USER_BUILD,
        'mode' : 0o2750,
    } , {
        'path' : SOLUTION_BUILD,
        'user_name' : USER_BUILD,
        'group_name' : GROUP_ALL,
        'mode' : 0o2750,
    } , {
        'path' : TOOL,
        'user_name' : USER_TEST,
        'group_name' : USER_TEST,
        'mode' : 0o2750,
    } , {
        'path' : TOOL+'/src',
        'user_name' : USER_TEST,
        'group_name' : USER_TEST,
        'mode' : 0o2750,
    } , {
        'path' : TOOL+'/build',
        'user_name' : USER_TEST,
        'group_name' : USER_TEST,
        'mode' : 0o2750,
    }
]
