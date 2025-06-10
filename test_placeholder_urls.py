#!/usr/bin/env python3
"""
Test placeholder image URLs to ensure they work correctly
"""

import requests
from gemini_client import GeminiClient


def test_placeholder_urls():
    """Test various placeholder image services"""
    
    print("🖼️  Testing Placeholder Image URLs")
    print("=" * 40)
    
    # Test URLs to check
    test_urls = [
        ("Placehold.co", "https://placehold.co/400x300/3B82F6/FFFFFF?text=Test"),
        ("Picsum Photos", "https://picsum.photos/400/300"),
        ("Unsplash Source", "https://source.unsplash.com/400x300/?abstract,blue"),
    ]
    
    for service_name, url in test_urls:
        try:
            print(f"\n🔍 Testing {service_name}: {url}")
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                print(f"   ✅ Working - Status: {response.status_code}")
                if 'content-type' in response.headers:
                    content_type = response.headers['content-type']
                    if 'image' in content_type:
                        print(f"   📸 Content Type: {content_type}")
                    else:
                        print(f"   ⚠️  Unexpected Content Type: {content_type}")
            else:
                print(f"   ❌ Failed - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
    
    return True


def test_gemini_client_urls():
    """Test GeminiClient image URL generation"""
    
    print("\n🤖 Testing GeminiClient Image Generation")
    print("=" * 40)
    
    client = GeminiClient()
    
    test_cases = [
        ('button', 'action button'),
        ('card', 'user profile'),
        ('table', 'data display'),
        ('unknown_type', 'fallback test')
    ]
    
    for component_type, context in test_cases:
        print(f"\n🎯 Component: {component_type}")
        
        # Test different sizes
        sizes = [(400, 300), (200, 150), (600, 400)]
        
        for width, height in sizes:
            try:
                url = client.generate_placeholder_image_url(component_type, context, width, height)
                print(f"   {width}x{height}: {url}")
                
                # Test if URL is reachable
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    print(f"      ✅ Accessible")
                else:
                    print(f"      ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Error generating or testing URL: {e}")
    
    return True


def test_popular_alternatives():
    """Test other popular placeholder services as alternatives"""
    
    print("\n🔄 Testing Alternative Placeholder Services")
    print("=" * 40)
    
    alternatives = [
        ("Lorem Picsum", "https://picsum.photos/400/300"),
        ("Placehold.co", "https://placehold.co/400x300"),
        ("Placehold.co with text", "https://placehold.co/400x300/blue/white?text=Hello"),
        ("DummyImage", "https://dummyimage.com/400x300/3B82F6/FFFFFF&text=Test"),
        ("Placeholder.com", "https://placeholder.com/400x300"),
    ]
    
    working_services = []
    
    for name, url in alternatives:
        try:
            print(f"\n🔍 {name}: {url}")
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                print(f"   ✅ Working")
                working_services.append((name, url))
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Summary: {len(working_services)}/{len(alternatives)} services working")
    
    if working_services:
        print("\n✅ Recommended working services:")
        for name, url in working_services:
            print(f"   - {name}: {url.split('?')[0]}...")
    
    return len(working_services) > 0


if __name__ == "__main__":
    try:
        print("🚀 Starting Placeholder URL Tests")
        
        success = True
        success &= test_placeholder_urls()
        success &= test_gemini_client_urls()
        success &= test_popular_alternatives()
        
        if success:
            print("\n🎉 Placeholder URL tests completed!")
            print("\n💡 Recommendations:")
            print("   - Placehold.co: Reliable, customizable colors and text")
            print("   - Picsum Photos: Beautiful random images")
            print("   - DummyImage: Simple, reliable, basic customization")
        else:
            print("\n⚠️  Some services may be unreliable")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()