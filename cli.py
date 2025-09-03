#!/usr/bin/env python3
"""
Command Line Interface for Eroge Translation Tool
Alternative to GUI for advanced users and automation
"""

import click
import os
import sys
from pathlib import Path
from core.config import ConfigManager
from core.translator import TranslationManager
from core.api_client import APIClient
from utils.test_utils import run_translation_test


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Eroge Translation Tool - Automatic translation for eroge games"""
    pass


@cli.command()
@click.option('--input-dir', '-i', required=True, help='Input directory containing JSON files')
@click.option('--output-dir', '-o', required=True, help='Output directory for translated files')
@click.option('--config', '-c', default='.env', help='Configuration file path')
@click.option('--backup/--no-backup', default=True, help='Create backup files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def translate(input_dir, output_dir, config, backup, verbose):
    """Translate RPG Maker game files"""
    
    if verbose:
        click.echo(f"Loading configuration from {config}")
    
    # Load configuration
    try:
        config_manager = ConfigManager(config)
        app_config = config_manager.get_config()
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)
    
    # Validate inputs
    if not os.path.exists(input_dir):
        click.echo(f"Error: Input directory does not exist: {input_dir}", err=True)
        sys.exit(1)
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    if verbose:
        click.echo(f"Input directory: {input_dir}")
        click.echo(f"Output directory: {output_dir}")
        click.echo(f"Model: {app_config.get('model', 'Unknown')}")
        click.echo(f"Target language: {app_config.get('language', 'English')}")
    
    # Start translation
    try:
        manager = TranslationManager(app_config, input_dir, output_dir)
        
        if verbose:
            # Connect progress signals for CLI output
            manager.progress_updated.connect(
                lambda current, total, filename: click.echo(f"Progress: {current}/{total} - {filename}")
            )
            manager.log_message.connect(lambda msg: click.echo(f"Log: {msg}"))
        
        click.echo("Starting translation...")
        manager.run()  # Run synchronously in CLI mode
        
        # Get usage stats
        stats = manager.api_client.get_usage_stats()
        click.echo(f"\\nTranslation completed!")
        click.echo(f"Tokens used: {stats['total_tokens']} (Input: {stats['input_tokens']}, Output: {stats['output_tokens']})")
        click.echo(f"Estimated cost: ${stats['total_cost']:.4f}")
        
    except Exception as e:
        click.echo(f"Translation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='.env', help='Configuration file path')
def test_api(config):
    """Test API connection"""
    
    try:
        config_manager = ConfigManager(config)
        app_config = config_manager.get_config()
        
        click.echo("Testing API connection...")
        
        api_client = APIClient(app_config)
        success, message = api_client.test_connection()
        
        if success:
            click.echo(f"✅ {message}")
        else:
            click.echo(f"❌ {message}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error testing API: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--api-key', prompt=True, hide_input=True, help='API key')
@click.option('--model', default='gpt-4', help='Model name')
@click.option('--language', default='English', help='Target language')
@click.option('--api-url', default='', help='Custom API URL (leave empty for OpenAI)')
@click.option('--provider', type=click.Choice(['openai', 'openrouter', 'anthropic', 'google', 'xai', 'deepseek', 'ollama', 'custom']), 
              default='openai', help='API provider')
@click.option('--config', '-c', default='.env', help='Configuration file path')
def setup(api_key, model, language, api_url, provider, config):
    """Setup initial configuration"""
    
    try:
        config_manager = ConfigManager(config)
        
        # Set API URL based on provider if not specified
        if not api_url:
            if provider == 'openrouter':
                api_url = 'https://openrouter.ai/api/v1'
            elif provider == 'anthropic':
                api_url = 'https://api.anthropic.com'
            elif provider == 'google':
                api_url = 'https://generativelanguage.googleapis.com/v1beta'
            elif provider == 'ollama':
                api_url = 'http://localhost:11434/v1'
        
        # Update configuration
        config_manager.set_value('key', api_key)
        config_manager.set_value('model', model)
        config_manager.set_value('language', language)
        config_manager.set_value('api', api_url)
        config_manager.set_value('provider', provider)
        
        # Auto-update pricing if model is in database
        from core.models import MODEL_DB
        pricing = MODEL_DB.get_pricing_for_model(model)
        config_manager.set_value('input_cost', str(pricing['input_cost']))
        config_manager.set_value('output_cost', str(pricing['output_cost']))
        
        # Save configuration
        config_manager.save_config()
        
        click.echo(f"Configuration saved to {config}")
        click.echo(f"Provider: {provider}")
        click.echo(f"Model: {model}")
        click.echo(f"Pricing: ${pricing['input_cost']:.4f} input, ${pricing['output_cost']:.4f} output per 1K tokens")
        
        # Test the configuration
        click.echo("Testing API connection...")
        api_client = APIClient(config_manager.get_config())
        success, message = api_client.test_connection()
        
        if success:
            click.echo(f"✅ Setup completed successfully!")
        else:
            click.echo(f"⚠️  Configuration saved, but API test failed: {message}")
            
    except Exception as e:
        click.echo(f"Setup failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='.env', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def test(config, verbose):
    """Run translation test with sample data"""
    
    try:
        config_manager = ConfigManager(config)
        app_config = config_manager.get_config()
        
        click.echo("Running translation test...")
        
        results = run_translation_test(app_config, verbose=verbose)
        
        if 'error' in results:
            click.echo(f"❌ Test failed: {results['error']}", err=True)
            sys.exit(1)
        else:
            click.echo("✅ Test completed successfully!")
            if verbose:
                for filename, result in results.items():
                    click.echo(f"  {filename}: {result}")
                    
    except Exception as e:
        click.echo(f"Test failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, help='Scan subdirectories')
def scan(directory, recursive):
    """Scan directory for translatable files"""
    
    from core.file_processor import FileProcessor
    
    processor = FileProcessor()
    
    click.echo(f"Scanning {directory} for translatable files...")
    
    if recursive:
        pattern = "**/*.json"
    else:
        pattern = "*.json"
    
    import glob
    json_files = glob.glob(os.path.join(directory, pattern), recursive=recursive)
    
    translatable_files = []
    total_japanese_strings = 0
    
    for file_path in json_files:
        try:
            stats = processor.get_file_stats(file_path)
            
            if stats.get('needs_translation', False):
                translatable_files.append((file_path, stats))
                total_japanese_strings += stats.get('japanese_text_entries', 0)
                
        except Exception as e:
            click.echo(f"Error processing {file_path}: {e}")
    
    click.echo(f"\\nFound {len(translatable_files)} translatable files:")
    
    for file_path, stats in translatable_files:
        rel_path = os.path.relpath(file_path, directory)
        japanese_count = stats.get('japanese_text_entries', 0)
        estimated_tokens = stats.get('estimated_tokens', 0)
        click.echo(f"  {rel_path}: {japanese_count} Japanese strings (~{estimated_tokens} tokens)")
    
    click.echo(f"\\nTotal: {total_japanese_strings} Japanese strings to translate")


@cli.command()
@click.option('--provider', type=click.Choice(['openai', 'anthropic', 'google', 'xai', 'deepseek', 'all']), 
              default='all', help='Filter by provider')
@click.option('--show-pricing', is_flag=True, help='Show pricing information')
def models(provider, show_pricing):
    """List available models"""
    
    from core.models import MODEL_DB, ModelProvider
    
    if provider == 'all':
        models_list = MODEL_DB.get_all_models()
        click.echo("All Available Models:")
    else:
        provider_enum = getattr(ModelProvider, provider.upper())
        models_list = MODEL_DB.get_models_by_provider(provider_enum)
        click.echo(f"{provider.title()} Models:")
    
    current_provider = None
    for model in sorted(models_list, key=lambda x: (x.provider.value, x.name)):
        if current_provider != model.provider.value:
            current_provider = model.provider.value
            click.echo(f"\\n--- {current_provider.upper()} ---")
        
        pricing_info = ""
        if show_pricing:
            pricing = MODEL_DB.get_pricing_for_model(model.name)
            pricing_info = f" (${pricing['input_cost']:.4f} in, ${pricing['output_cost']:.4f} out per 1K)"
        
        click.echo(f"  {model.name}: {model.display_name}{pricing_info}")
        if show_pricing:
            click.echo(f"    Context: {model.context_length:,} tokens")
            click.echo(f"    Description: {model.description}")


@cli.command()
@click.option('--config', '-c', default='.env', help='Configuration file path')
def status(config, verbose):
    """Show current configuration and status"""
    
    try:
        config_manager = ConfigManager(config)
        app_config = config_manager.get_config()
        
        click.echo("Configuration Status:")
        click.echo(f"  Config file: {config}")
        click.echo(f"  API URL: {app_config.get('api', '(OpenAI)') or '(OpenAI)'}")
        click.echo(f"  Model: {app_config.get('model', 'Not set')}")
        click.echo(f"  Language: {app_config.get('language', 'Not set')}")
        click.echo(f"  Timeout: {app_config.get('timeout', 'Not set')}s")
        click.echo(f"  File threads: {app_config.get('fileThreads', 'Not set')}")
        click.echo(f"  Translation threads: {app_config.get('threads', 'Not set')}")
        click.echo(f"  Batch size: {app_config.get('batchsize', 'Not set')}")
        
        # Check if API key is set
        if app_config.get('key'):
            click.echo(f"  API Key: ✅ Set")
        else:
            click.echo(f"  API Key: ❌ Not set")
        
        # Validate configuration
        valid, message = config_manager.validate_config()
        
        if valid:
            click.echo(f"\\nStatus: ✅ {message}")
        else:
            click.echo(f"\\nStatus: ❌ {message}")
            
    except Exception as e:
        click.echo(f"Error reading configuration: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
