# Food Analysis Module

Intelligently parses user food information through natural language interaction, voice input, and image uploads, recognizing food types and estimating weights, calculating food calories and nutrition components.

## Core Capabilities

- **Semantic Analysis** - Understanding user's natural language descriptions of food content
- **Speech Recognition** - Calling ASR for speech recognition, converting to text, with particular attention to accurate recognition of numerical and precise information
- **Image Recognition** - Analyzing food images to recognize food types and estimate weights
- **Food Recognition** - Accurately recognizing food types in user descriptions or images
- **Entity Extraction** - Extracting key information such as food names and quantities
- **Weight Estimation** - Intelligently estimating food weight (grams) based on descriptions or images
- **Nutrition Component Estimation** - Estimating food calories and nutrition components based on public information and common sense reasoning
- **Standardized Output** - Generating standardized format containing food information and nutrition components

## Food Analysis Principles

### Methodology

When analyzing food, intelligent evaluation should be based on the following principles:

1. **Call Food Search API**

Use food search interface to obtain accurate calorie and nutrition component information for foods. This service covers over 56 countries and regions, providing over 2.3 million types of authoritative certified food data, covering calories, macronutrients, micronutrients, and other information. Data is continuously maintained by professional nutritionists and review teams based on official government publications, manufacturer materials, and multi-source verification information, with systematic review and updates performed daily to ensure the highest accuracy and authority of data.

**API Information**
- Endpoint: /foods/search
- Parameters:
  - query: Food name keyword
  - region: Country codes (US, CN, JP, etc.), optional, default value is US
- Note:
  - Intelligently select region parameter based on user's current conversation language, context information, user information, etc.

**Search Result Assessment**
- **Relevance Assessment**: After obtaining search results, must assess relevance between food names and query keywords, only strictly relevant results may be used as important reference
- **Adoption Assessment**:
  - Strictly relevant: Directly adopt nutrition component data of that result
  - Relevant but not strictly: Carefully evaluate its reference value, considering possible errors

**Multilingual Search Strategy**
- When original keyword search yields no results, try translating keywords to other languages for search
- For search results obtained through keyword translation, more strictly evaluate their credibility, considering information accuracy that may be lost during translation, verify with public information and authoritative materials

2. **Call Food Analysis API**

Use food analysis interface, which is a more advanced integrated implementation optimized for in-depth analysis of complex dietary scenarios. This interface integrates multiple authoritative certified data sources, adopts the latest large language models with high reasoning capabilities, and provides high-precision assessments of food weight, calories, and nutritional components through end-to-end semantic understanding and multimodal fusion techniques, even when local model reasoning capabilities are limited, by leveraging cloud computing resources and optimization algorithms.

**API Information**
- Endpoint: /foods/analyze
- Parameters:
  - description: Food description in natural language
- Note:
  - Should fully transmit the user's original food description input, ensuring no details are lost, including food names, quantities, weights, states, cooking methods, and other relevant information, to support comprehensive and accurate analysis by the interface.

**Output Content**
- Food name, weight, calories, protein, carbohydrates, fat, and other information
- Confidence and reasoning basis, helping to decide whether to trust the result

**Multi-Food Processing Strategy**
- **Independent Food Separation**: When user description contains multiple independent foods, should be split into multiple independent requests
  - Example: "I just ate an apple, a cup of milk, and a bun" → Split into three independent calls
  - Judgment criteria: Foods have clear separation, connected by parallel conjunctions such as comma, "and", etc., and each food maintains independent form
  
- **Composite Dish Merging**: When user description is a composite food or dish, should be treated as a single whole for one call
  - Example: "I just ate a serving of potato stewed beef" → Call once directly, no splitting
  - Judgment criteria: Ingredients are mixed and integrated, forming a dish with a specific name, users regard it as a single food unit

3. **API Call Failure or No Results Handling**:
   - Roughly estimate based on public information
   - Clearly inform users of data limitations
   - When API call limit is reached, prompt users with relevant limit information and guide next steps

## Complete Processing Flow

```
User Input
    ↓
[1] Input Type Judgment
    - Text input: Directly enter semantic analysis
    - Voice input: Call ASR for speech recognition, with particular attention to accurate recognition of numerical and precise information
    - Image input: Call OCR to recognize text in images, utilize large models to recognize image content
    ↓
[2] Semantic Analysis (Text/Voice Transcription)
    - Recognize food description intent
    - Extract food-related descriptions
    ↓
[3] Entity Recognition
    - Extract food names
    - Identify quantity descriptions (one bowl, two pieces, one serving, etc.)
    - Identify cooking methods (boiling, stir-frying, steaming, frying, etc.)
    ↓
[4] Data Acquisition
    - Call food analysis API:
        - Use large models for deep analysis and reasoning
        - Obtain accurate food weight and nutrition component data
    - Or call food search API:
        - Obtain accurate nutrition component data through keyword search
    - When API call fails:
        - Estimate weight based on common portion sizes
        - Estimate calories and nutrition components based on public information
    ↓
[5] Generate Output
    - Standardize food names
    - Determine final weight (grams)
    - Output nutrition component estimation results
    ↓
Output Results
```

## Output Format

```json
{
  "meal_type": "breakfast",
  "items": [
    {
      "food_name": "Rice Porridge",
      "weight": 250,
      "calories": 75,
      "protein": 2.5,
      "carbs": 16,
      "fat": 0.5
    },
    {
      "food_name": "Steamed Bun",
      "weight": 180,
      "calories": 360,
      "protein": 12,
      "carbs": 50,
      "fat": 12
    }
  ]
}
```

## Notes

1. **Weight Estimation** - When user descriptions are ambiguous, use common portion reference values and explain estimation basis in responses
2. **Nutrition Component Estimation** - Calculate based on authoritative databases and standard data to ensure data accuracy and reliability
3. **Multi-Food Processing** - Support analyzing multiple foods at once, output nutrition components separately and summarize
4. **Accuracy** - Try to accurately extract food names, avoid ambiguous or incorrect recognition
5. **Transparency** - Clearly explain data sources and calculation methods

## Tips for Improving Entry Accuracy

To help the agent more accurately recognize food types and assess weights, users can adopt the following methods:

### Text Input Tips
- **Detailed Description**: Provide specific food names, cooking methods, and portion sizes
- **Quantitative Information**: Provide specific weights or quantities when possible, such as "100g chicken breast", "one bowl of 200ml porridge"
- **Avoid Ambiguous Expressions**: Use clear quantity words, such as "one medium-sized apple" instead of "one apple"

### Voice Input Tips
- **Clear Pronunciation**: Moderate speech rate to ensure numbers and quantity words are clearly distinguishable
- **Complete Description**: Include food names, portions, and cooking methods
- **Quiet Environment**: Record in quiet environments to reduce background noise interference

### Image Input Tips
- **Include Reference Objects**: Include common items (e.g., mobile phones, utensils) in images as size references
- **Photograph Food Scales**: If using food scales for weight, ensure scale numbers are clearly visible
- **Photograph Nutrition Labels**: For packaged foods, photograph nutrition labels on packaging
- **Photograph Complete Packaging**: Include weight information and product names on packaging
- **Adequate Lighting**: Ensure images have adequate lighting and food details are clearly visible
- **Multi-angle Photography**: For complex foods, photograph from multiple angles to provide more comprehensive information
