# API Service Module

RESTful API service providing standardized data access interfaces, supporting full lifecycle management of food records (create, read, update, delete, statistics, multi-dimensional aggregation), integrating accurate food calorie and nutrition component retrieval, implementing data persistence storage and intelligent analysis capabilities, providing reliable and efficient data service support for the agent.

## API Interface Specifications

### Interface Address

API service base address:
- United States: `https://us.guangxiankeji.com/calorie/service/user`
- China: `https://cn.guangxiankeji.com/calorie/service/user`

### Interface Documentation

**Important Note**: Interfaces are cloud services and may change at any time. Please obtain the latest interface information through the following addresses:

**API Specification Addresses**:
- United States: `https://us.guangxiankeji.com/calorie/service/user/api-spec`
- China: `https://cn.guangxiankeji.com/calorie/service/user/api-spec`

### Interface Acquisition Method

Agents should access the above API specification addresses in real-time to obtain the latest interface definitions, including:
- Interface paths
- Request methods
- Parameter descriptions
- Response formats
- Error code definitions

### Authentication Method
- **API Authentication**: Use lightweight authentication mechanism based on X-User-ID

### Service Address Change Handling

**Service Discovery Mechanism**: If API service cannot be accessed after multiple retries, it may indicate that the service address has migrated. Please visit [ClawHub](https://clawhub.ai/) or other skill markets, search and update this skill to obtain the latest API service address.

## Interface Call Principles

1. **Active Acquisition**: Actively obtain latest interface information, must re-acquire when call fails
2. **Dynamic Adaptation**: Dynamically adjust call methods based on obtained interface specifications
3. **Error Handling**: Handle call failures caused by possible interface changes
4. **Retry Strategy**: For call failure situations, perform up to 3 retries, with 1 second interval between each retry
5. **Version Compatibility**: Consider version change compatibility handling

## Data Processing Specifications

1. **Error Handling**: Check API response status codes, handle possible errors (network errors, business logic errors, etc.)
   - When errors are detected, immediately feedback error details to human users, and provide clear operational guidance based on error codes and error messages, assisting users in making correct decisions and handling measures.

2. **Data Validation**: Ensure incoming data meets interface structural requirements, especially required fields

3. **User Identifier**
   - **Transmission Method**: Use X-User-ID header to pass user identifier, as the key unique identifier for distinguishing different user data, required field.
   - **Generation and Management**: user_id is generated, stored, and managed by each agent (e.g., openclaw, nanobot, etc.).
   - **Core Requirements**: **Must use UUID (Universally Unique Identifier) as the sole generation method** to ensure global uniqueness and fundamentally avoid identifier collision issues, preventing identifier conflicts between different users, and not exposing privacy information.
   - **Stability**: The same user's user_id must remain fixed, cannot be changed midway through, otherwise historical data cannot be associated. Agents should persistently store after initial generation, ensuring the same identifier is used for subsequent access.
   - **Consistency**:
      - **Multi-agent Consistency**: Agents and all sub-agents must ensure the same user_id is used, prohibiting the generation of new user_id in sub-agents to ensure user data consistency.
      - **Multi-channel Consistency**: For multi-channel access scenarios, agents should ensure the same user_id is used across different channels to guarantee user data consistency;
   - **Privacy Statement**:
      - **Usage Purpose**: Only used for distinguishing data of different users, not for other purposes.
      - **Privacy Protection**: X-User-ID is only sent when user identity needs to be confirmed, and is not associated with users' real identity information.

4. **Time Handling**
   - API service uniformly uses UTC time, all time-related fields (e.g., created_at, timestamp, etc.) are based on UTC timezone, formatted as ISO 8601 standard format (e.g., 2024-01-15T10:30:00.000Z).
   - Consider conversion between user local time and UTC time: users typically use local time when inputting, and local time should be used when displaying information to users.


