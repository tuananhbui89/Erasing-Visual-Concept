import os
import glob
import pandas as pd
from pathlib import Path


PUBLIC_URL = "https://www.dropbox.com/scl/fo/67lupmpbty4jgovpl2mm3/ADEbYnFbqFVVosNgtQH80QA?rlkey=f6mj267ogod40m38vixzi5gyd&st=kvvp9re9&dl=0"
LOCAL_PATH = "./"

def get_image_url_prefix(use_online_hosting=None):
    """
    Determine whether to use online hosting or local paths for images.
    
    Args:
        use_online_hosting: If None, will try to auto-detect. If True/False, will use that setting.
    
    Returns:
        The appropriate URL prefix for image sources
    """
    if use_online_hosting is None:
        # Auto-detect: check if we're generating for online hosting
        # You can modify this logic based on your needs
        # For now, let's check if PUBLIC_URL is set and valid
        use_online_hosting = PUBLIC_URL and PUBLIC_URL.startswith("http")
    
    if use_online_hosting:
        # For Dropbox, we need to modify the URL to get direct access
        if "dropbox.com" in PUBLIC_URL:
            # Convert Dropbox share URL to direct access format
            base_url = PUBLIC_URL.replace("?dl=0", "").replace("/fo/", "/fi/") + "/"
            return base_url
        else:
            return PUBLIC_URL.rstrip('/') + '/'
    else:
        return LOCAL_PATH

def generate_html_visualization(target_concept, df, paths, use_online_hosting=None):
    """Generate HTML visualization for a specific target concept"""
    
    # Filter dataframe for this target concept
    concept_df = df[df['target_concept'] == target_concept]
    
    # Find matching images for this concept
    matching_images = []
    
    for _, row in concept_df.iterrows():
        # Create filename using the template
        filename = f"{row['target_concept']}_id{row['prompt_id']}_seed{row['seed']}.jpg"
        
        # Check if image exists in all three folders
        sd_path = os.path.join('visualizations', 'data', 'sd', filename)
        uce_path = os.path.join('visualizations', 'data', 'uce', filename)
        our_path = os.path.join('visualizations', 'data', 'our', filename)
        
        if os.path.exists(sd_path) and os.path.exists(uce_path) and os.path.exists(our_path):
            matching_images.append({
                'filename': filename,
                'sd_path': f'data/sd/{filename}',  # Relative path for HTML
                'uce_path': f'data/uce/{filename}',  # Relative path for HTML
                'our_path': f'data/our/{filename}',  # Relative path for HTML
                'prompt_id': row['prompt_id'],
                'prompt': row['prompt'],
                'seed': row['seed']
            })
    
    print(f"Found {len(matching_images)} matching images for {target_concept}")
    
    if not matching_images:
        print(f"No matching images found for {target_concept}, skipping...")
        return None
    
    # Generate HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_concept} - SD vs UCE vs our Comparison</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .header .concept-name {{
            font-size: 24px;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 10px;
        }}
        .stats {{
            font-size: 18px;
            color: #666;
            margin-bottom: 20px;
        }}
        .navigation {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .nav-button {{
            display: inline-block;
            padding: 10px 20px;
            margin: 0 10px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }}
        .nav-button:hover {{
            background-color: #2980b9;
        }}
        .image-grid {{
            display: grid;
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }}
        .image-trio {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .image-container {{
            text-align: center;
        }}
        .image-container h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 18px;
            font-weight: bold;
        }}
        .image-container.sd h3 {{
            color: #27ae60;
        }}
        .image-container.uce h3 {{
            color: #e74c3c;
        }}
        .image-container.our h3 {{
            color: #9b59b6;
        }}
        .image-container img {{
            max-width: 100%;
            max-height: 350px;
            border: 2px solid #ddd;
            border-radius: 8px;
            object-fit: contain;
            transition: transform 0.3s;
        }}
        .image-container img:hover {{
            transform: scale(1.05);
            border-color: #3498db;
        }}
        .image-info {{
            margin-top: 15px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            text-align: left;
        }}
        .image-info .filename {{
            font-size: 14px;
            color: #666;
            word-break: break-all;
            margin-bottom: 5px;
        }}
        .image-info .prompt {{
            font-size: 13px;
            color: #444;
            font-style: italic;
            margin-bottom: 5px;
        }}
        .image-info .details {{
            font-size: 12px;
            color: #888;
        }}
        @media (max-width: 1200px) {{
            .image-trio {{
                grid-template-columns: 1fr 1fr;
            }}
            .image-container:nth-child(3) {{
                grid-column: 1 / -1;
                max-width: 50%;
                margin: 0 auto;
            }}
        }}
        @media (max-width: 768px) {{
            .image-trio {{
                grid-template-columns: 1fr;
            }}
            .image-container:nth-child(3) {{
                grid-column: auto;
                max-width: 100%;
            }}
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            color: #666;
        }}
        .method-legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        .legend-color.sd {{ background-color: #27ae60; }}
        .legend-color.uce {{ background-color: #e74c3c; }}
        .legend-color.our {{ background-color: #9b59b6; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SD vs UCE vs our Image Comparison</h1>
        <div class="concept-name">{target_concept}</div>
        <div class="stats">
            <strong>{len(matching_images)} matching image triplets found</strong>
        </div>
        <div class="method-legend">
            <div class="legend-item">
                <div class="legend-color sd"></div>
                <span>SD (Original)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color uce"></div>
                <span>UCE</span>
            </div>
            <div class="legend-item">
                <div class="legend-color our"></div>
                <span>Our</span>
            </div>
        </div>
    </div>
    
    <div class="navigation">
        <a href="../index.html" class="nav-button">← Back to All Concepts</a>
    </div>
    
    <div class="image-grid">
"""
    
    # Get the appropriate URL prefix for images
    url_prefix = get_image_url_prefix(use_online_hosting)
    
    # Add each image trio
    for i, image_data in enumerate(matching_images):
        html_content += f"""
        <div class="image-trio">
            <div class="image-container sd">
                <h3>SD (Original)</h3>
                <img src="{url_prefix}{image_data['sd_path']}" alt="SD - {image_data['filename']}" onerror="this.style.display='none'">
                <div class="image-info">
                    <div class="filename">{image_data['filename']}</div>
                    <div class="prompt">"{image_data['prompt']}"</div>
                    <div class="details">Prompt ID: {image_data['prompt_id']} | Seed: {image_data['seed']}</div>
                </div>
            </div>
            <div class="image-container uce">
                <h3>UCE</h3>
                <img src="{url_prefix}{image_data['uce_path']}" alt="UCE - {image_data['filename']}" onerror="this.style.display='none'">
                <div class="image-info">
                    <div class="filename">{image_data['filename']}</div>
                    <div class="prompt">"{image_data['prompt']}"</div>
                    <div class="details">Prompt ID: {image_data['prompt_id']} | Seed: {image_data['seed']}</div>
                </div>
            </div>
            <div class="image-container our">
                <h3>Our</h3>
                <img src="{url_prefix}{image_data['our_path']}" alt="our - {image_data['filename']}" onerror="this.style.display='none'">
                <div class="image-info">
                    <div class="filename">{image_data['filename']}</div>
                    <div class="prompt">"{image_data['prompt']}"</div>
                    <div class="details">Prompt ID: {image_data['prompt_id']} | Seed: {image_data['seed']}</div>
                </div>
            </div>
        </div>
"""
    
    html_content += """
    </div>
    
    <div class="footer">
        <p>Generated automatically from SD, UCE, and our comparison data</p>
    </div>
</body>
</html>
"""
    
    # Create output directory if it doesn't exist
    os.makedirs('visualizations', exist_ok=True)
    
    # Write HTML file to visualizations directory
    safe_concept_name = target_concept.replace(' ', '_').replace('/', '_')
    output_file = f'visualizations/{safe_concept_name}.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML visualization saved as '{output_file}'")
    return output_file

def generate_index_page(target_concepts, concept_stats):
    """Generate an index page linking to all concept visualizations"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SD vs UCE vs our - All Concepts</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            font-size: 18px;
        }}
        .method-legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        .legend-color.sd {{ background-color: #27ae60; }}
        .legend-color.uce {{ background-color: #e74c3c; }}
        .legend-color.our {{ background-color: #9b59b6; }}
        .concepts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .concept-card {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        .concept-card:hover {{
            transform: translateY(-5px);
        }}
        .concept-name {{
            font-size: 24px;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 10px;
        }}
        .concept-stats {{
            color: #666;
            margin-bottom: 15px;
        }}
        .view-button {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }}
        .view-button:hover {{
            background-color: #2980b9;
        }}
        .summary {{
            text-align: center;
            margin: 30px 0;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SD vs UCE vs Our Method - Concept Erasure</h1>
        <p>Interactive visualization of concept erasure results across three methods</p>
        <div class="method-legend">
            <div class="legend-item">
                <div class="legend-color sd"></div>
                <span>SD (Original Stable Diffusion)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color uce"></div>
                <span>UCE (Unified Concept Editing)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color our"></div>
                <span>Our</span>
            </div>
        </div>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>{len(target_concepts)} concepts</strong> with <strong>{sum(concept_stats.values())} total image triplets</strong></p>
    </div>
    
    <div class="concepts-grid">
"""
    
    # Add each concept card
    for concept in sorted(target_concepts):
        safe_concept_name = concept.replace(' ', '_').replace('/', '_')
        image_count = concept_stats.get(concept, 0)
        
        html_content += f"""
        <div class="concept-card">
            <div class="concept-name">{concept}</div>
            <div class="concept-stats">{image_count} image triplets</div>
            <a href="visualizations/{safe_concept_name}.html" class="view-button">View Comparison</a>
        </div>
"""
    
    html_content += """
    </div>
    
    <div style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated automatically from SD, UCE, and our comparison data</p>
    </div>
</body>
</html>
"""
    
    # Write index file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Index page saved as 'index.html'")

def main():
    # Define paths for all three folders
    paths = {
        'SD': 'visualizations/data/sd/*target_concept*_id*prompt_id*_seed*seed*.jpg',
        'UCE': 'visualizations/data/uce/*target_concept*_id*prompt_id*_seed*seed*.jpg',
        'our': 'visualizations/data/our/*target_concept*_id*prompt_id*_seed*seed*.jpg'
    }
    
    # Determine hosting mode - auto-detect or allow manual override
    # You can modify this logic or add command line arguments as needed
    use_online_hosting = False  # Auto-detect
    
    # Optional: Check for command line argument
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['online', 'dropbox', 'public']:
            use_online_hosting = True
        elif sys.argv[1].lower() in ['local', 'offline']:
            use_online_hosting = False
    
    # Auto-detect if not specified
    if use_online_hosting is None:
        use_online_hosting = PUBLIC_URL and PUBLIC_URL.startswith("http")
    
    print(f"🔗 Hosting mode: {'Online (Dropbox)' if use_online_hosting else 'Local'}")
    if use_online_hosting:
        print(f"📡 Using public URL: {PUBLIC_URL}")
    else:
        print(f"📁 Using local path: {LOCAL_PATH}")
    
    # Read the prompt file
    prompt_file = 'visualizations/data/all_prompts.csv'
    
    try:
        df = pd.read_csv(prompt_file)
        print(f"Loaded {len(df)} records from {prompt_file}")
    except FileNotFoundError:
        print(f"Error: File '{prompt_file}' not found!")
        return
    
    # Get all unique target concepts
    target_concepts = df['target_concept'].unique()
    print(f"Found {len(target_concepts)} unique target concepts: {', '.join(target_concepts)}")
    
    # Generate HTML files for each concept
    concept_stats = {}
    
    for concept in target_concepts:
        print(f"\nProcessing concept: {concept}")
        output_file = generate_html_visualization(concept, df, paths, use_online_hosting)
        
        if output_file:
            # Count images for this concept
            concept_df = df[df['target_concept'] == concept]
            matching_count = 0
            
            for _, row in concept_df.iterrows():
                filename = f"{row['target_concept']}_id{row['prompt_id']}_seed{row['seed']}.jpg"
                sd_path = os.path.join('visualizations', 'data', 'sd', filename)
                uce_path = os.path.join('visualizations', 'data', 'uce', filename)
                our_path = os.path.join('visualizations', 'data', 'our', filename)
                
                if os.path.exists(sd_path) and os.path.exists(uce_path) and os.path.exists(our_path):
                    matching_count += 1
            
            concept_stats[concept] = matching_count
    
    # Generate index page
    print(f"\nGenerating index page...")
    generate_index_page(target_concepts, concept_stats)
    
    print(f"\n✅ Complete! Generated visualizations for {len(target_concepts)} concepts")
    print(f"📁 Open 'index.html' in your browser to explore all concepts")
    print(f"📊 Total image triplets processed: {sum(concept_stats.values())}")
    
    if use_online_hosting:
        print(f"\n🔗 Online hosting mode:")
        print(f"   Images will be loaded from: {get_image_url_prefix(use_online_hosting)}")
        print(f"   Upload all HTML files and the data folder to your hosting service")
    else:
        print(f"\n💻 Local hosting mode:")
        print(f"   Images will be loaded from local paths")
        print(f"   Ensure the data folder is in the same directory as the HTML files")

if __name__ == "__main__":
    main() 