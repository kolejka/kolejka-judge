# vim:ts=4:sts=4:sw=4:expandtab

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

GROUP_MAIN = 'satori-judge-main'
GROUP_ALL  = 'satori-judge'

USER_TEST = 'satori-judge-test'
USER_COMPILE = 'satori-judge-comp'
USER_TOOL = 'satori-judge-tool'
USER_EXEC = 'satori-judge-exec'

SYSTEM_GROUPS = [
    GROUP_MAIN,
]
SYSTEM_USERS = [
    {
        'user_name' : USER_TEST,
        'home' : 'home/'+USER_TEST,
        'groups' : [ GROUP_MAIN, GROUP_ALL, ],
    } , {
        'user_name' : USER_COMPILE,
        'home' : 'home/'+USER_COMPILE,
        'groups' : [ GROUP_MAIN, GROUP_ALL, ],
    } , {
        'user_name' : USER_TOOL,
        'home' : 'home/'+USER_TOOL,
        'groups' : [ GROUP_MAIN, GROUP_ALL, ],
    } , {
        'user_name' : USER_EXEC,
        'home' : 'home/'+USER_EXEC,
        'groups' : [ GROUP_ALL, ],
    }
]
SYSTEM_DIRECTORIES = [
    {
        'path' : TEST,
        'user_name' : USER_TEST,
        'group_name' : USER_TEST,
        'mode' : 0o750,
    } , {
        'path' : SOLUTION,
        'user_name' : USER_TEST,
        'group_name' : GROUP_ALL,
        'mode' : 0o750,
    } , {
        'path' : SOLUTION_SOURCE,
        'user_name' : USER_TEST,
        'group_name' : GROUP_MAIN,
        'mode' : 0o750,
    } , {
        'path' : SOLUTION_BUILD,
        'user_name' : USER_COMPILE,
        'group_name' : GROUP_ALL,
        'mode' : 0o750,
    } , {
        'path' : TOOL,
        'user_name' : USER_TEST,
        'group_name' : GROUP_MAIN,
        'mode' : 0o750,
    } , {
        'path' : TOOL_SOURCE,
        'user_name' : USER_TEST,
        'group_name' : GROUP_MAIN,
        'mode' : 0o750,
    } , {
        'path' : TOOL_BUILD,
        'user_name' : USER_TOOL,
        'group_name' : GROUP_MAIN,
        'mode' : 0o750,
    }
]
