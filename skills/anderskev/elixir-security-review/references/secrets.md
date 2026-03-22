# Secret Management

## Never Hardcode Secrets

```elixir
# CRITICAL - secrets in source code
defmodule MyApp.API do
  @api_key "sk_live_abc123"  # Committed to git!

  def call do
    HTTPClient.get(url, headers: [{"Authorization", @api_key}])
  end
end
```

## Use Environment Variables

### Runtime Configuration

```elixir
# config/runtime.exs
import Config

config :my_app,
  api_key: System.fetch_env!("API_KEY"),
  database_url: System.fetch_env!("DATABASE_URL")
```

### Application Config

```elixir
# In code
def api_key do
  Application.fetch_env!(:my_app, :api_key)
end
```

### System.get_env at Runtime

```elixir
# For values that might change
def feature_flag do
  System.get_env("FEATURE_ENABLED", "false") == "true"
end
```

## Config File Security

### Never Commit Secrets

```elixir
# config/dev.exs - OK, no real secrets
config :my_app, api_key: "dev_test_key"

# config/prod.exs - NO secrets here!
config :my_app, api_key: System.get_env("API_KEY")

# config/runtime.exs - secrets loaded at runtime
import Config

if config_env() == :prod do
  config :my_app,
    api_key: System.fetch_env!("API_KEY")
end
```

### .gitignore

```gitignore
# Ignore secret files
config/*.secret.exs
.env
*.pem
*.key
```

## Secret Rotation

### Support Multiple Keys

```elixir
defmodule MyApp.Crypto do
  def current_key_id, do: System.get_env("CURRENT_KEY_ID", "1")

  def keys do
    %{
      "1" => System.fetch_env!("ENCRYPTION_KEY_1"),
      "2" => System.get_env("ENCRYPTION_KEY_2")
    }
  end

  def encrypt(data) do
    key_id = current_key_id()
    encrypted = do_encrypt(data, keys()[key_id])
    {key_id, encrypted}
  end

  def decrypt({key_id, encrypted}) do
    do_decrypt(encrypted, keys()[key_id])
  end
end
```

## Logging

### Never Log Secrets

```elixir
# BAD
Logger.info("Connecting with key: #{api_key}")

# GOOD
Logger.info("Connecting to API")

# GOOD - redact in inspect
defmodule APIClient do
  defstruct [:url, :api_key]

  defimpl Inspect do
    def inspect(%{url: url}, _opts) do
      "#APIClient<url: #{url}, api_key: [REDACTED]>"
    end
  end
end
```

## Review Questions

1. Are any secrets hardcoded in source files?
2. Are secrets loaded from environment at runtime?
3. Are secret files excluded from git?
4. Are secrets redacted from logs?
