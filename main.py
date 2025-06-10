#!/usr/bin/env python3
"""
Main application for OpenUI + CrewAI + Gemini integration
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from crew_agents import ComponentCreationCrew
import json
import time
import argparse


def save_result(result, filename="component_result.json"):
    """Save the component creation result to a file"""
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"💾 Result saved to {filename}")


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Create amazing React components using OpenUI + CrewAI + Gemini')
    parser.add_argument('--requirements', '-r', 
                        default="Create a beautiful user profile card with avatar, name, title, bio, and action buttons. Include hover animations and professional icons.",
                        help='Component requirements description')
    parser.add_argument('--iterations', '-i', type=int, default=2,
                        help='Maximum number of refinement iterations')
    parser.add_argument('--output', '-o', default="component_result.json",
                        help='Output file for results')
    parser.add_argument('--pure', action='store_true',
                        help='Use PURE framework analyst (Purposeful, Usable, Readable, Extensible)')
    parser.add_argument('--framework', choices=['standard', 'pure'], default='standard',
                        help='Analysis framework to use (standard or pure)')
    
    args = parser.parse_args()
    
    # Determine which framework to use
    use_pure = args.pure or args.framework == 'pure'
    
    print("🎨 OpenUI + CrewAI + Gemini Component Creator")
    print("=" * 50)
    print(f"Requirements: {args.requirements}")
    print(f"Max iterations: {args.iterations}")
    print(f"Analysis framework: {'PURE' if use_pure else 'Standard'}")
    print()
    
    # Initialize the crew with chosen framework
    crew = ComponentCreationCrew(use_pure_framework=use_pure)
    
    # Create the component
    start_time = time.time()
    result = crew.create_component(args.requirements, max_iterations=args.iterations)
    end_time = time.time()
    
    if result:
        print("\n" + "=" * 50)
        print("🎉 COMPONENT CREATION COMPLETED!")
        print("=" * 50)
        print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
        print(f"📊 Final score: {result['final_score']}/10")
        print(f"🔄 Iterations completed: {result['iterations']}")
        print(f"📝 Component length: {len(result['component_code'])} characters")
        print()
        
        print("📋 FINAL COMPONENT:")
        print("-" * 30)
        print(result['component_code'][:1000] + "..." if len(result['component_code']) > 1000 else result['component_code'])
        print()
        
        # Save result
        save_result(result, args.output)
        
        return True
    else:
        print("\n❌ Component creation failed!")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Application completed successfully!")
    else:
        print("\n💥 Application failed!")
        exit(1)
