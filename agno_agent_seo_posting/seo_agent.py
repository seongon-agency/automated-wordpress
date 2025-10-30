"""
SEO Blog Publishing Agent - Main Implementation
Conversational AI agent for converting Google Docs to SEO-optimized HTML
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import dotenv

# Agno framework imports
from agno.agent import Agent
from agno.models.anthropic import Claude

# Import our custom tools
from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images
from tools.html_formatter import format_html_with_template
from tools.wordpress_publisher import publish_to_wordpress

# Import utilities
from utils.html_extractor import extract_title_from_content


# Load environment variables
dotenv.load_dotenv()


# Define input models for the agent
class GoogleDocsInput(BaseModel):
    """Input model for Google Docs processing."""
    content_url: str = Field(..., description="URL of the content Google Doc")
    template_url: str = Field(..., description="URL of the template Google Doc")
    post_title: Optional[str] = Field(None, description="Title for the blog post")
    process_images: bool = Field(True, description="Whether to process and resize images")
    target_width: int = Field(800, description="Target width for images in pixels")


class WordPressConfig(BaseModel):
    """Configuration for WordPress publishing."""
    site_url: str = Field(..., description="WordPress site URL")
    post_title: str = Field(..., description="Blog post title")
    post_status: str = Field("draft", description="Post status: draft or publish")
    categories: Optional[list] = Field(None, description="Category IDs")
    tags: Optional[list] = Field(None, description="Tag names")


class SEOBlogAgent:
    """Main SEO Blog Publishing Agent."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SEO Blog Agent.

        Args:
            api_key: Anthropic API key (uses environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        # Storage for conversation state
        self.state = {
            "content_html": None,
            "template_html": None,
            "processed_html": None,
            "formatted_html": None,
            "image_metadata": [],
            "template_rules": {},
            "extracted_title": None
        }

        # Create the agent
        self.agent = Agent(
            name="SEO Blog Publishing Assistant",
            role="Expert at converting Google Docs to SEO-optimized HTML",
            model=Claude(id="claude-sonnet-4-5-20250929", api_key=self.api_key),
            description=(
                "You are an expert SEO blog publishing assistant. "
                "You help users convert Google Docs into beautifully formatted, "
                "SEO-optimized HTML and optionally publish to WordPress."
            ),
            instructions=[
                "Always be friendly, professional, and clear in your communication.",
                "Guide users step-by-step through the blog publishing workflow.",
                "Explain what you're doing at each stage of the process.",
                "TWO Google Docs are required: one for content and one for the HTML template.",
                "The template Google Doc defines the formatting rules (paragraph styles, image classes, etc.).",
                "Provide helpful tips about SEO and blog formatting when appropriate.",
                "Always show a preview or summary before finalizing.",
                "Ask for confirmation before publishing to WordPress.",
                "Be proactive in identifying potential issues (missing images, broken links, etc.).",
                "Provide the final HTML in a format that's easy to copy and use."
            ],
            markdown=True,
            debug_mode=False
        )

    def process_documents(
        self,
        content_url: str,
        template_url: str,
        post_title: Optional[str] = None,
        process_images_flag: bool = True,
        target_width: int = 800
    ) -> Dict[str, Any]:
        """
        Process the Google Docs: convert to HTML, apply template, process images.

        Args:
            content_url: URL of the content Google Doc
            template_url: URL of the template Google Doc
            post_title: Optional post title
            process_images_flag: Whether to process images
            target_width: Target width for image resizing

        Returns:
            Dictionary with processing results
        """
        results = {
            "success": False,
            "stage": None,
            "content_html": None,
            "template_html": None,
            "formatted_html": None,
            "final_html": None,
            "image_metadata": [],
            "errors": [],
            "extracted_title": None
        }

        # Step 1: Convert content Google Doc to HTML
        print("📄 Step 1: Converting content Google Doc to HTML...")
        content_result = google_docs_to_html(content_url)

        if not content_result['success']:
            results['errors'].append(f"Content conversion failed: {content_result['error']}")
            results['stage'] = "content_conversion"
            return results

        results['content_html'] = content_result['raw_html']
        self.state['content_html'] = content_result['raw_html']
        print(f"✅ Content converted: {content_result['name']}")

        # Extract title from content (h1 heading)
        extracted_title = extract_title_from_content(
            content_result['raw_html'],
            fallback=post_title
        )
        if extracted_title:
            results['extracted_title'] = extracted_title
            self.state['extracted_title'] = extracted_title
            print(f"📝 Extracted title: \"{extracted_title}\"")

        # Step 2: Convert template Google Doc to HTML
        print("\n📐 Step 2: Converting template Google Doc to HTML...")
        template_result = google_docs_to_html(template_url)

        if not template_result['success']:
            results['errors'].append(f"Template conversion failed: {template_result['error']}")
            results['stage'] = "template_conversion"
            return results

        results['template_html'] = template_result['raw_html']
        self.state['template_html'] = template_result['raw_html']
        print(f"✅ Template converted: {template_result['name']}")

        # Step 3: Process images (if requested)
        current_html = results['content_html']

        if process_images_flag:
            print(f"\n🖼️  Step 3: Processing images (target width: {target_width}px)...")
            image_result = process_images(
                html_content=current_html,
                target_width=target_width
            )

            if image_result['success']:
                current_html = image_result['processed_html']
                results['image_metadata'] = image_result['image_metadata']
                self.state['image_metadata'] = image_result['image_metadata']
                print(f"✅ Processed {len(image_result['image_metadata'])} images")
            else:
                results['errors'].append(f"Image processing warning: {image_result['error']}")
                print(f"⚠️  Image processing had issues: {image_result['error']}")

        results['processed_html'] = current_html
        self.state['processed_html'] = current_html

        # Step 4: Apply template formatting
        print("\n✨ Step 4: Applying template formatting to content...")
        format_result = format_html_with_template(
            content_html=current_html,
            template_html=results['template_html']
        )

        if not format_result['success']:
            results['errors'].append(f"Formatting failed: {format_result['error']}")
            results['stage'] = "formatting"
            return results

        results['formatted_html'] = format_result['formatted_html']
        results['final_html'] = format_result['formatted_html']
        self.state['formatted_html'] = format_result['formatted_html']
        self.state['template_rules'] = format_result['template_rules']
        print("✅ Template formatting applied successfully")

        results['success'] = True
        results['stage'] = "complete"
        return results

    def publish_to_wp(
        self,
        formatted_html: str,
        post_title: str,
        wordpress_site_url: str,
        post_status: str = "draft",
        categories: Optional[list] = None,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Publish the formatted HTML to WordPress.

        Args:
            formatted_html: Final formatted HTML
            post_title: Post title
            wordpress_site_url: WordPress site URL
            post_status: "draft" or "publish"
            categories: Category IDs
            tags: Tag names

        Returns:
            Dictionary with publishing results
        """
        print("\n🚀 Publishing to WordPress...")

        # Get image paths for upload
        image_paths = []
        image_metadata = []

        for img in self.state.get('image_metadata', []):
            if 'local_path' in img and img['local_path']:
                image_paths.append(img['local_path'])
                image_metadata.append({
                    'alt': img.get('alt', ''),
                    'title': img.get('alt', ''),
                    'description': img.get('alt', ''),
                    'caption': img.get('alt', '')
                })

        # Publish
        result = publish_to_wordpress(
            formatted_html=formatted_html,
            wordpress_site_url=wordpress_site_url,
            post_title=post_title,
            post_status=post_status,
            categories=categories,
            tags=tags,
            image_paths=image_paths if image_paths else None,
            image_metadata=image_metadata if image_metadata else None
        )

        if result['success']:
            print(f"✅ Published successfully!")
            print(f"🔗 Post URL: {result['post_url']}")
        else:
            print(f"❌ Publishing failed: {result['error']}")

        return result

    def save_html_to_file(self, html_content: str, filename: str = "output.html") -> str:
        """
        Save HTML content to a file.

        Args:
            html_content: HTML to save
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = os.path.join(os.getcwd(), filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"💾 HTML saved to: {output_path}")
        return output_path

    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("\n" + "="*80)
        print("🎯 SEO Blog Publishing Agent")
        print("="*80)
        print("\nWelcome! I'll help you convert Google Docs to SEO-optimized HTML.")
        print("\nYou'll need TWO Google Docs:")
        print("  1. 📄 Content Doc - Your blog post content")
        print("  2. 📐 Template Doc - HTML formatting template")
        print("\n💡 Tip: The first heading (h1) in your content will be used as the post title!")
        print("\n" + "="*80 + "\n")

        # Get content URL
        content_url = input("Enter the Content Google Docs URL: ").strip()
        if not content_url:
            print("❌ Content URL is required!")
            return

        # Get template URL
        template_url = input("Enter the Template Google Docs URL: ").strip()
        if not template_url:
            print("❌ Template URL is required!")
            return

        # Get post title (optional - will be auto-extracted from h1)
        post_title = input("Enter post title override (optional, press Enter to auto-extract from content): ").strip()

        # Ask about image processing
        process_imgs = input("Process and resize images? (y/n, default: y): ").strip().lower()
        process_images_flag = process_imgs != 'n'

        target_width = 800
        if process_images_flag:
            width_input = input("Target image width in pixels (default: 800): ").strip()
            if width_input.isdigit():
                target_width = int(width_input)

        # Process documents
        print("\n" + "="*80)
        print("🔄 Processing documents...")
        print("="*80 + "\n")

        results = self.process_documents(
            content_url=content_url,
            template_url=template_url,
            post_title=post_title,
            process_images_flag=process_images_flag,
            target_width=target_width
        )

        if not results['success']:
            print(f"\n❌ Processing failed at stage: {results['stage']}")
            for error in results['errors']:
                print(f"   - {error}")
            return

        # Show preview
        print("\n" + "="*80)
        print("✅ Processing Complete!")
        print("="*80)

        # Display extracted title
        if results.get('extracted_title'):
            print(f"\n📝 Post Title: \"{results['extracted_title']}\"")

        print(f"\nFinal HTML length: {len(results['final_html'])} characters")
        print(f"Images processed: {len(results['image_metadata'])}")
        print("\n" + "-"*80)
        print("HTML Preview (first 500 characters):")
        print("-"*80)
        print(results['final_html'][:500])
        print("-"*80)

        # Save to file
        save_file = input("\n💾 Save HTML to file? (y/n, default: y): ").strip().lower()
        if save_file != 'n':
            filename = input("Enter filename (default: output.html): ").strip()
            if not filename:
                filename = "output.html"
            self.save_html_to_file(results['final_html'], filename)

        # Track WordPress URL for final summary
        wordpress_url = None

        # Ask about WordPress publishing
        publish = input("\n🚀 Publish to WordPress? (y/n, default: n): ").strip().lower()
        if publish == 'y':
            wp_url = input("WordPress site URL: ").strip()

            # Use extracted title if available, otherwise ask for it
            default_title = results.get('extracted_title') or post_title
            if default_title:
                print(f"Using extracted title: \"{default_title}\"")
                use_extracted = input("Use this title? (y/n, default: y): ").strip().lower()
                if use_extracted == 'n':
                    wp_title = input("Enter custom post title: ").strip()
                else:
                    wp_title = default_title
            else:
                wp_title = input("Post title: ").strip()

            wp_status = input("Post status (draft/publish, default: draft): ").strip() or "draft"

            wp_result = self.publish_to_wp(
                formatted_html=results['final_html'],
                post_title=wp_title,
                wordpress_site_url=wp_url,
                post_status=wp_status
            )

            if wp_result['success']:
                wordpress_url = wp_result['post_url']
                print("\n" + "="*80)
                print("🎉 SUCCESSFULLY PUBLISHED TO WORDPRESS!")
                print("="*80)
                print(f"\n📌 Post ID: {wp_result['post_id']}")
                print(f"📊 Status: {wp_result['status'].upper()}")
                print(f"\n🔗 ACCESS YOUR POST HERE:")
                print(f"   {wp_result['post_url']}")
                print("\n" + "="*80)
            else:
                print(f"\n❌ Publishing failed: {wp_result.get('error', 'Unknown error')}")

        print("\n" + "="*80)
        print("✨ Done! Thank you for using SEO Blog Publishing Agent.")
        print("="*80)

        # Final summary
        if wordpress_url:
            print("\n📋 SESSION SUMMARY:")
            print(f"   ✅ Post published to WordPress")
            print(f"   🔗 URL: {wordpress_url}")

        print()


def main():
    """Main entry point."""
    try:
        agent = SEOBlogAgent()
        agent.run_interactive()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
