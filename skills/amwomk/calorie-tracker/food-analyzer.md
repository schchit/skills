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

## Food Weight Estimation Principles

### Estimation Methodology

When estimating food weight, intelligent evaluation should be based on the following principles:

1. **Based on Common Sense and Public Data**: Reference typical portion data from food nutrition databases, dietary guidelines, and industry standards, combined with food physical characteristics for estimation.

2. **Consider Portion Description Semantics**: Accurately understand portion modifier words in user descriptions (e.g., "small bowl", "large portion", "small amount"), and judge actual portion size based on context.

3. **Comprehensive Food Characteristics**: Consider factors affecting weight such as food type, form, density, and water content. For example:
   - Liquid or semi-liquid foods (porridge, soup noodles) need to consider broth ratio
   - Foods with skin/bone/seed need to estimate edible portion ratio
   - Cooking methods affect food weight changes (e.g., frying increases weight, baking reduces water)

4. **Based on Edible Portion Estimation**: All weight estimation must be based on edible portion (net weight). For foods with skin, bones, seeds, or shells, non-edible parts must be removed for calculation, including but not limited to:
   - Fruits: peels (e.g., orange peel, banana peel), seeds (e.g., apple core, peach pit)
   - Meats: bones (e.g., rib bones, chicken bones), fascia, fat (if explicitly stated by users)
   - Nuts: hard shells (e.g., peanut shells, sunflower seeds shells, walnut shells)
   - Other non-edible parts: fish bones, shrimp shells, eggshells, etc.

5. **Prioritize Explicit Numerical Values**: If users provide specific weight or packaging specifications (e.g., "250ml milk", "100g chicken breast"), directly use that value.

6. **Image Recognition Weight Estimation**:
   - **Food Scale Priority**: If the image contains a food scale, prioritize using the number displayed on the scale as weight
   - **Nutrition Label Priority**: If the image contains a nutrition label on food packaging, prioritize using the nutrition data provided in the label
   - **Packaging Weight Priority**: If the food packaging in the image has weight information, prioritize using that value
   - **Reference Object Estimation**: Use reference objects in images (e.g., mobile phones, utensils) size to estimate food weight

7. **Estimation Uncertainty**: For ambiguous descriptions, request clarification from users when necessary to ensure result accuracy and reliability.

### Estimation Accuracy Requirements

- Prioritize authoritative data sources
- For composite foods or mixed dishes, decompose main ingredients and estimate separately
- Estimation results should indicate whether it is "net weight" or "with packaging/container weight"
- Maintain consistency and interpretability of estimation logic
- All food weight estimation must be accurate and reliable

## Nutrition Component Estimation Principles

### Estimation Methodology

When estimating food nutrition components, intelligent evaluation should be based on the following principles:

1. **Prioritize Calling Food Search Interface**: Prioritize using food search interface provided by API service to obtain accurate calorie and nutrition component information for foods. This service covers over 56 countries and regions, providing over 2.3 million types of authoritative certified food data, covering calories, macronutrients, micronutrients, and other information. Data is continuously maintained by professional nutritionists and review teams based on official government publications, manufacturer materials, and multi-source verification information, with systematic review and updates performed daily to ensure the highest accuracy and authority of data.
   - query parameter is food name keyword
   - region parameter is country codes such as US, CN, JP, optional, default value is US
   - Intelligently select region parameter based on user's current conversation language, context information, user information, etc.
   - **Search Result Relevance Assessment**: After obtaining search results, must assess relevance between food names and query keywords, only strictly relevant results may be used as important reference.
   - **Result Adoption Assessment**:
      - When food name in search results is strictly relevant to query keywords, directly adopt nutrition component data of that result.
      - When food name in search results is relevant but not strictly relevant to query keywords, carefully evaluate its reference value, considering possible errors.
   - **Multilingual Search Strategy**: When original keyword search yields no results, try translating keywords to other languages for search.
   - **Translation Result Assessment**: For search results obtained through keyword translation, more strictly evaluate their credibility, considering information accuracy that may be lost during translation, verify with public information and authoritative materials.

2. When food search interface call fails or no results:
   - Estimate food calories and nutrition components based on public information

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
[4] Weight Estimation
    - Text/Voice input: Estimate weight based on quantity descriptions
    - Image input:
        - Prioritize using numbers displayed on food scale
        - Prioritize using nutrition label data
        - Prioritize using weight information on packaging
        - Use reference objects to estimate weight
    - Reference common portion equivalent table
    - Consider cooking method impact on weight
    ↓
[5] Nutrition Component Estimation
    - **Mandatory priority to query accurate nutrition component information through API service**
    - Consider cooking method impact on nutrition components
    - Calculate final nutrition component content
    ↓
[6] Generate Output
    - Standardize food names
    - Determine final weight (grams)
    - Output nutrition component estimation results
    ↓
Output Results
```

## Intent Recognition Rules

### Food Description Intent
- Keywords: ate, drank, breakfast, lunch, dinner, snack, ate, drank
- Examples:
  - "I ate porridge and two buns for breakfast" → Extract porridge and buns
  - "Just drank a cup of coffee" → Extract coffee
  - "Ate beef noodles for lunch" → Extract beef noodles

### Food Query Intent
- Keywords: query, nutrition, calories, protein, carbohydrates, fat
- Examples:
  - "How many calories in an apple" → Extract apple
  - "Nutrition components of chicken breast" → Extract chicken breast

## Entity Extraction Strategy

### Food Entities
- Staple foods: rice, noodles, steamed buns, porridge, bread
- Proteins: eggs, chicken, beef, pork, fish, tofu
- Vegetables: greens, broccoli, tomatoes, cucumbers, carrots
- Fruits: apples, bananas, oranges, grapes, watermelons
- Beverages: milk, soy milk, coffee, tea, fruit juice

### Quantity Entities
- Quantity words: one, two, one bowl, one cup, one serving
- Weight units: grams, jin, liang, kilograms
- Volume units: milliliters, liters, cups, bowls

## Output Format

### Standard Output Format

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

### Simplified Output Format

- Rice Porridge: 250g, approximately 75kcal calories, 2.5g protein, 16g carbohydrates, 0.5g fat
- Steamed Bun: 180g, approximately 360kcal calories, 12g protein, 50g carbohydrates, 12g fat
- Apple: 180g, approximately 95kcal calories, 0.5g protein, 25g carbohydrates, 0.3g fat

## Notes

1. **Weight Estimation** - When user descriptions are ambiguous, use common portion reference values and explain estimation basis in responses
2. **Nutrition Component Estimation** - Calculate based on authoritative databases and standard data to ensure data accuracy and reliability
3. **Multiple Food Processing** - Support analyzing multiple foods at once, output nutrition components separately and summarize
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
