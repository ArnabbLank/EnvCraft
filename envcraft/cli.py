import sys
import argparse
from pathlib import Path
from importlib import import_module

# Add current directory to path so we can import user's config
if str(Path.cwd()) not in sys.path:
    sys.path.insert(0, str(Path.cwd()))


def find_config_class():
    """Try to find EnvCraft subclass in common locations"""
    from envcraft import EnvCraft
    
    search_paths = [
        "config.AppConfig",
        "app.config.AppConfig", 
        "settings.Settings",
        "config.Config",
        "config_example.AppConfig",
        "examples.config_example.AppConfig",
    ]
    
    for path in search_paths:
        try:
            module_name, class_name = path.rsplit(".", 1)
            module = import_module(module_name)
            config_class = getattr(module, class_name)
            
            # Verify it's an EnvCraft subclass
            if issubclass(config_class, EnvCraft):
                return config_class
        except (ImportError, AttributeError, TypeError):
            continue
    
    return None


def cmd_check(args):
    """Check configuration status"""
    config_class = find_config_class()
    if not config_class:
        print("❌ Could not find EnvCraft subclass")
        print("   Searched: config.AppConfig, app.config.AppConfig, settings.Settings")
        sys.exit(1)
    
    is_valid = config_class.diagnose()
    sys.exit(0 if is_valid else 1)


def cmd_generate(args):
    """Generate .env.example file"""
    config_class = find_config_class()
    if not config_class:
        print("❌ Could not find EnvCraft subclass")
        sys.exit(1)
    
    output = args.output or ".env.example"
    config_class.generate_example(output)


def cmd_docs(args):
    """Generate configuration documentation"""
    config_class = find_config_class()
    if not config_class:
        print("❌ Could not find EnvCraft subclass")
        sys.exit(1)
    
    output = args.output or "CONFIG.md"
    config_class.generate_docs(output)


def cmd_explain(args):
    """Explain a specific environment variable"""
    config_class = find_config_class()
    if not config_class:
        print("❌ Could not find EnvCraft subclass")
        sys.exit(1)
    
    var_name = args.variable.lower()
    
    for field_name, field_info in config_class.model_fields.items():
        if field_name.lower() == var_name:
            env_name = field_name.upper()
            print(f"\n📝 {env_name}\n")
            
            if field_info.description:
                print(f"  Description: {field_info.description}")
            
            type_str = str(field_info.annotation).replace('typing.', '').replace('envcraft.config.', '')
            print(f"  Type: {type_str}")
            
            if field_info.is_required():
                print(f"  Required: Yes")
            else:
                print(f"  Required: No")
                if field_info.default is not None and field_info.default != ...:
                    print(f"  Default: {field_info.default}")
            
            print()
            return
    
    print(f"❌ Variable '{args.variable}' not found in config")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="envcraft",
        description="Environment configuration management tool"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # check command
    parser_check = subparsers.add_parser("check", help="Validate configuration")
    parser_check.set_defaults(func=cmd_check)
    
    # generate command
    parser_generate = subparsers.add_parser("generate", help="Generate .env.example")
    parser_generate.add_argument("-o", "--output", help="Output file (default: .env.example)")
    parser_generate.set_defaults(func=cmd_generate)
    
    # docs command
    parser_docs = subparsers.add_parser("docs", help="Generate configuration documentation")
    parser_docs.add_argument("-o", "--output", help="Output file (default: CONFIG.md)")
    parser_docs.set_defaults(func=cmd_docs)
    
    # explain command
    parser_explain = subparsers.add_parser("explain", help="Explain an environment variable")
    parser_explain.add_argument("variable", help="Variable name to explain")
    parser_explain.set_defaults(func=cmd_explain)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
