#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Image Generator
Generate images via HuggingFace (free) or OpenAI DALL-E API (paid)
"""

import os
import sys
import io
from datetime import datetime
from pathlib import Path
import argparse

# Set output encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_api_keys():
    """Load API keys (OpenAI and Hugging Face) from configs"""
    keys = {
        'openai': None,
        'huggingface': None
    }
    
    # Check environment variables
    keys['openai'] = os.getenv('OPENAI_API_KEY')
    keys['huggingface'] = os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_TOKEN')
    
    # Check .env file
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    keys['openai'] = keys['openai'] or line.strip().split('=', 1)[1]
                elif line.startswith('HUGGINGFACE_API_KEY=') or line.startswith('HF_TOKEN='):
                    keys['huggingface'] = keys['huggingface'] or line.strip().split('=', 1)[1]
    
    # Check ~/.cursor/cli-config.json
    cursor_config = Path.home() / '.cursor' / 'cli-config.json'
    if cursor_config.exists():
        try:
            import json
            with open(cursor_config, 'r') as f:
                config = json.load(f)
                if 'env' in config:
                    keys['openai'] = keys['openai'] or config['env'].get('OPENAI_API_KEY')
                    keys['huggingface'] = keys['huggingface'] or config['env'].get('HUGGINGFACE_API_KEY') or config['env'].get('HF_TOKEN')
        except Exception:
            pass
    
    return keys


def generate_image_huggingface(prompt, hf_token, model="black-forest-labs/FLUX.1-schnell", output_dir="~/Downloads"):
    """
    Generate image via Hugging Face Inference API (FREE!)
    
    Args:
        prompt: Text description of the image
        hf_token: Hugging Face API token
        model: HuggingFace model name
        output_dir: Directory to save the image
    
    Returns:
        Path to saved file or None on error
    """
    import requests
    
    print(f"🎨 Generating image via Hugging Face...")
    print(f"📝 Prompt: {prompt}")
    print(f"🤖 Model: {model}")
    print(f"💰 Cost: FREE!")
    print()
    
    try:
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=30
        )
        
        if response.status_code == 503:
            print("⏳ Model is loading on HuggingFace servers, this may take ~20 seconds...")
            import time
            time.sleep(20)
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=30)
        
        if response.status_code != 200:
            error_msg = response.json().get('error', 'Unknown error')
            print(f"❌ HuggingFace API error: {error_msg}")
            return None
        
        image_data = response.content
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(c if (c.isascii() and (c.isalnum() or c in (' ', '-', '_'))) else '_' for c in prompt[:50])
        safe_prompt = safe_prompt.strip().replace(' ', '_')
        filename = f"{timestamp}_HF_{safe_prompt}.png"
        
        # Save
        output_dir_expanded = Path(output_dir).expanduser()
        output_path = output_dir_expanded / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        print(f"✅ Successfully saved: {output_path}")
        print(f"💰 Cost: $0.00 (free)")
        
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error generating via HuggingFace: {e}")
        return None


def generate_image_openai(prompt, api_key, size="1024x1024", quality="standard", model="dall-e-2", output_dir="~/Downloads"):
    """
    Generate image via OpenAI DALL-E API (paid)
    
    Args:
        prompt: Text description of the image
        api_key: OpenAI API key
        size: Image size (1024x1024, 1792x1024, 1024x1792 for DALL-E 3)
        quality: Quality (standard or hd)
        model: Model (dall-e-3 or dall-e-2)
        output_dir: Directory to save the image
    
    Returns:
        Path to saved file or None on error
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    print(f"🎨 Generating image via OpenAI DALL-E...")
    print(f"📝 Prompt: {prompt}")
    print(f"📐 Size: {size}")
    print(f"✨ Quality: {quality}")
    print(f"🤖 Model: {model}")
    print()
    
    try:
        # Create API request
        request_params = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": 1,
        }
        
        # Quality parameter is only supported in DALL-E 3
        if model == "dall-e-3":
            request_params["quality"] = quality
        
        response = client.images.generate(**request_params)
        
        # Get image URL
        image_url = response.data[0].url
        
        # Download image
        import requests
        image_data = requests.get(image_url).content
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Keep only ASCII characters, digits and basic punctuation
        safe_prompt = "".join(c if (c.isascii() and (c.isalnum() or c in (' ', '-', '_'))) else '_' for c in prompt[:50])
        safe_prompt = safe_prompt.strip().replace(' ', '_')
        filename = f"{timestamp}_{safe_prompt}.png"
        
        # Save
        # Expand ~ to full path
        output_dir_expanded = Path(output_dir).expanduser()
        output_path = output_dir_expanded / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        print(f"✅ Successfully saved: {output_path}")
        print(f"🔗 Original URL: {image_url}")
        
        # Cost information
        if model == "dall-e-3":
            cost = 0.04 if quality == "standard" else 0.08
            if size in ["1792x1024", "1024x1792"]:
                cost *= 2
        else:  # dall-e-2
            cost = 0.02 if size == "1024x1024" else 0.018
        
        print(f"💰 Request cost: ${cost:.3f}")
        
        return str(output_path)
        
    except Exception as e:
        import traceback
        print(f"❌ Error generating via OpenAI: {e}")
        print("\nError details:")
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Image generator via HuggingFace (free) or OpenAI DALL-E (paid)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  # Free via HuggingFace (default)
  python generate_image.py "Cat in space with pizza"
  
  # Explicitly use DALL-E
  python generate_image.py "Sunset over mountains" --provider openai
  python generate_image.py "Abstract art" --provider openai --quality hd --model dall-e-3
        """
    )
    
    parser.add_argument(
        'prompt',
        type=str,
        help='Description of the image to generate'
    )
    
    parser.add_argument(
        '--provider',
        type=str,
        default='huggingface',
        choices=['auto', 'huggingface', 'openai'],
        help='Generation provider: auto (try HF first, suggest OpenAI on fail), huggingface (HF only), openai (DALL-E only). Default: huggingface'
    )
    
    parser.add_argument(
        '--hf-model',
        type=str,
        default='black-forest-labs/FLUX.1-schnell',
        help='HuggingFace model (default: FLUX.1-schnell)'
    )
    
    parser.add_argument(
        '--size',
        type=str,
        default='1024x1024',
        choices=['1024x1024', '1792x1024', '1024x1792', '256x256', '512x512'],
        help='Image size for DALL-E (default: 1024x1024)'
    )
    
    parser.add_argument(
        '--quality',
        type=str,
        default='standard',
        choices=['standard', 'hd'],
        help='Image quality (DALL-E 3 only, default: standard)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='dall-e-2',
        choices=['dall-e-3', 'dall-e-2'],
        help='DALL-E model for generation (default: dall-e-2)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='~/Downloads',
        help='Folder to save images (default: ~/Downloads)'
    )
    
    args = parser.parse_args()
    
    # Load API keys
    api_keys = load_api_keys()
    
    result = None
    
    # Provider selection logic
    if args.provider == 'auto' or args.provider == 'huggingface':
        # Try HuggingFace
        if api_keys['huggingface']:
            result = generate_image_huggingface(
                prompt=args.prompt,
                hf_token=api_keys['huggingface'],
                model=args.hf_model,
                output_dir=args.output_dir
            )
            
            if result:
                sys.exit(0)  # Successfully generated via HF
            
            # HF failed
            if args.provider == 'huggingface':
                # User explicitly requested HF only - exit with error
                print("\n❌ Failed to generate via HuggingFace")
                sys.exit(1)
            else:
                # provider='auto' - suggest OpenAI but don't call it automatically
                print("\n❌ HuggingFace generation failed")
                print("\n💡 You can try paid OpenAI DALL-E API:")
                print(f'   python3 generate_image.py "{args.prompt}" --provider openai')
                print("\n💰 Cost: ~$0.02-0.04 per image (DALL-E 2/3)")
                print("ℹ️  Requires OPENAI_API_KEY in ~/.cursor/cli-config.json")
                sys.exit(1)
        else:
            # No HF token
            if args.provider == 'huggingface':
                print("❌ HuggingFace token not found!")
                print("Add HF_TOKEN to ~/.cursor/cli-config.json:")
                print('{"env": {"HF_TOKEN": "your_token"}}')
                print("\nGet token: https://huggingface.co/settings/tokens")
                sys.exit(1)
            else:
                # provider='auto' but no HF token - suggest OpenAI
                print("⚠️  HuggingFace token not found")
                print("\n💡 You can try paid OpenAI DALL-E API:")
                print(f'   python3 generate_image.py "{args.prompt}" --provider openai')
                print("\n💰 Cost: ~$0.02-0.04 per image")
                print("ℹ️  Requires OPENAI_API_KEY in ~/.cursor/cli-config.json")
                sys.exit(1)
    
    # Explicit OpenAI request
    if args.provider == 'openai':
        if not api_keys['openai']:
            print("\n❌ OpenAI API key not found!")
            print("Add OPENAI_API_KEY to ~/.cursor/cli-config.json:")
            print('{"env": {"OPENAI_API_KEY": "sk-your-key"}}')
            print("\nGet key: https://platform.openai.com/api-keys")
            sys.exit(1)
        
        # Validate parameters for DALL-E
        if args.model == 'dall-e-2' and args.quality == 'hd':
            print("⚠️  Warning: DALL-E 2 doesn't support HD quality, using standard")
            args.quality = 'standard'
        
        if args.model == 'dall-e-2' and args.size in ['1792x1024', '1024x1792']:
            print("⚠️  Warning: DALL-E 2 doesn't support large sizes, using 1024x1024")
            args.size = '1024x1024'
        
        result = generate_image_openai(
            prompt=args.prompt,
            api_key=api_keys['openai'],
            size=args.size,
            quality=args.quality,
            model=args.model,
            output_dir=args.output_dir
        )
        
        if result:
            sys.exit(0)
        else:
            print("\n❌ Failed to generate image")
            sys.exit(1)


if __name__ == '__main__':
    main()
