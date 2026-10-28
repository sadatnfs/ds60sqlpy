# Parse and format text without evaluating learner code or loading startup files.
using JuliaFormatter

function parse_source(source)
    parsed = Meta.parseall(source)
    function validate(node)
        if node isa Expr
            node.head in (:error, :incomplete) && error("Invalid Julia source")
            foreach(validate, node.args)
        end
    end
    validate(parsed)
    function semantic(node)
        if node isa Expr
            return Expr(
                node.head,
                (semantic(child) for child in node.args if !(child isa LineNumberNode))...,
            )
        elseif node isa QuoteNode
            return QuoteNode(semantic(node.value))
        end
        return node
    end
    return semantic(parsed)
end

function main()
    length(ARGS) == 1 && ARGS[1] in ("parse", "format", "lint") ||
        error("Choose parse, format or lint")
    source = read(stdin, String)
    ncodeunits(source) <= 5_000_000 && !occursin('\0', source) || error("Source exceeds limits")
    isvalid(source) || error("Source must be valid UTF-8")
    before = parse_source(source)
    ARGS[1] == "parse" && return
    formatted = format_text(source; margin = 100, indent = 4, format_docstrings = false)
    isequal(before, parse_source(formatted)) || error("Formatter changed parsed expressions")
    if ARGS[1] == "lint"
        any(line -> occursin(r"[ \t]+$", line), split(source, '\n')) && error("Trailing whitespace")
        return
    end
    print(rstrip(formatted, ['\r', '\n']), '\n')
end

try
    main()
catch exception
    showerror(stderr, exception)
    println(stderr)
    exit(1)
end
