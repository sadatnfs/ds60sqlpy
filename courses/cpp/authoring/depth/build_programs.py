"""Render standalone worked examples without changing learner pads or official references."""
from pathlib import Path
import json,re,textwrap
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'courses/cpp'
INPUT=Path(__file__).with_name('program_inputs.json')
HEADERS={
'algorithm':('std::sort','std::count','std::max','std::min','std::reverse','std::ranges::sort'),
'atomic':('std::atomic',), 'cassert':('assert(',), 'charconv':('std::from_chars',),
'chrono':('std::chrono',), 'cmath':('std::abs',), 'concepts':('std::integral',),
'condition_variable':('std::condition_variable',), 'cstddef':('std::size_t',),
'filesystem':('std::filesystem',), 'fstream':('std::ifstream','std::ofstream'),
'future':('std::promise','std::future','std::async','std::launch'), 'iostream':('std::cout','std::cerr'),
'limits':('std::numeric_limits',), 'map':('std::map',), 'memory':('std::unique_ptr','std::make_unique'),
'mutex':('std::mutex','std::unique_lock','std::lock_guard'), 'numeric':('std::accumulate',),
'optional':('std::optional','std::nullopt'), 'queue':('std::queue',), 'ranges':('std::views','std::ranges'),
'span':('std::span',), 'sstream':('std::istringstream','std::ostringstream'),
'stdexcept':('std::invalid_argument','std::runtime_error','std::out_of_range'),
'string':('std::string','std::getline',), 'string_view':('std::string_view',),
'system_error':('std::errc',), 'thread':('std::thread','std::this_thread'),
'type_traits':('std::is_',), 'utility':('std::move','std::forward'),
'variant':('std::variant','std::get<','std::holds_alternative'), 'vector':('std::vector',),
}

def format_definition(code):
    # Only whitespace changes: preserve quoted strings and for-loop semicolons.
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|[{};()]|[^{};()"\']+',code)
    output='';depth=0;paren=0
    for token in tokens:
        if token=='(':paren+=1
        elif token==')':paren-=1
        if token=='{':
            output+=' {\n';depth+=1;output+='    '*depth
        elif token=='}':
            depth-=1;output=output.rstrip()+'\n'+'    '*depth+'}'
        elif token==';' and paren==0:output+=';\n'+'    '*depth
        else:output+=token
    return output.strip()

for record in json.loads(INPUT.read_text()):
    n=record['number']
    for index,body in enumerate(record['program_bodies'],1):
        main=body+f'\nstd::cout << "cpp-{n:03d} example {index} checks passed\\n";\nreturn 0;'
        defs=format_definition(record['definitions'])
        content=defs+'\nint main() {\n'+textwrap.indent(main,'    ')+'\n}\n'
        headers=[name for name,patterns in HEADERS.items() if any(p in content for p in patterns)]
        source=''.join(f'#include <{name}>\n' for name in sorted(headers))+'\n'+content
        destination=BASE/f'examples/cpp-{n:03d}-example-{index}.cpp'
        destination.parent.mkdir(exist_ok=True);destination.write_text(source)
