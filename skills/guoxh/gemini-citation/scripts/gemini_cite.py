import os
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Query Gemini with Google Search Grounding for exact citations.")
    parser.add_argument("query", help="The research query to run")
    parser.add_argument("--model", default="gemini-2.5-pro", help="The Gemini model to use")
    parser.add_argument("--format", default="text", choices=["text", "json"], help="Output format")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
        
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package is not installed. Run 'pip install google-genai'", file=sys.stderr)
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    # Enable Google Search grounding
    # We ask the model explicitly to provide APA citations
    prompt = (
        f"Research the following topic: {args.query}\n"
        "Provide a detailed, evidence-based response.\n"
        "Crucially, you must format all references as proper APA citations at the end, "
        "and use inline citations (e.g., Author, Year) in the text. "
        "Rely strictly on the grounded search results."
    )
    
    try:
        response = client.models.generate_content(
            model=args.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                temperature=0.2
            )
        )
        
        # Extract grounding metadata if available
        grounding_metadata = None
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "grounding_metadata"):
                grounding_metadata = candidate.grounding_metadata
                
        if args.format == "json":
            sources = []
            if grounding_metadata and hasattr(grounding_metadata, "grounding_chunks"):
                for chunk in grounding_metadata.grounding_chunks:
                    if hasattr(chunk, "web"):
                        sources.append({
                            "title": getattr(chunk.web, "title", "Unknown Title"),
                            "uri": getattr(chunk.web, "uri", "Unknown URI")
                        })
            
            output = {
                "text": response.text,
                "sources": sources
            }
            print(json.dumps(output, indent=2))
        else:
            print(response.text)
            print("\n--- Grounding Sources ---")
            if grounding_metadata and hasattr(grounding_metadata, "grounding_chunks"):
                for i, chunk in enumerate(grounding_metadata.grounding_chunks):
                    if hasattr(chunk, "web"):
                        title = getattr(chunk.web, "title", "Unknown Title")
                        uri = getattr(chunk.web, "uri", "Unknown URI")
                        print(f"[{i+1}] {title} - {uri}")
            else:
                print("No search grounding metadata returned by the API.")
                
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
