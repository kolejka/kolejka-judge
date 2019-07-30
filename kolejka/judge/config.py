# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)

DISTRIBUTION_ADDRESS = 'https://kolejka.matinf.uj.edu.pl/KolejkaJudge.zip'

LOG = 'log'

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
