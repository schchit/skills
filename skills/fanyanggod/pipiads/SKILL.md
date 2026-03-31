---
name: pipiads
description: Search and analyze ads, products, stores across TikTok and Facebook using PipiAds advertising intelligence API. Find trending ads, track competitors, discover winning products, monitor ad campaigns, and perform AI-powered image search.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - PIPIADS_API_KEY
      bins:
        - npm
    install:
      command: npm
      args:
        - install
        - -g
        - "pipiads-mcp-server@1.0.3"
    primaryEnv: PIPIADS_API_KEY
    emoji: "📊"
    homepage: https://www.pipiads.com
    mcpServers:
      pipiads:
        command: pipiads-mcp-server
        env:
          PIPIADS_API_KEY: "{{PIPIADS_API_KEY}}"
---

# PipiAds - Advertising Intelligence

Search and analyze advertising data across TikTok and Facebook platforms.

## Setup

1. Get your API key at [pipiads.com](https://www.pipiads.com)
2. Set the environment variable: `PIPIADS_API_KEY`

## Available Tools (73 total)

### Ad Spy
- `search_ads` — Search ad videos across TikTok and Facebook by keyword, region, platform, engagement metrics, ad spend, delivery days
- `get_ad_detail` — Get detailed info for a specific ad by video ID

### Ad Products
- `search_products` — Search e-commerce products advertised on TikTok/Facebook
- `get_product_detail` — Get product detail including images, price, landing page, Shopify data
- `search_adlibrary_products` — Search Meta Ad Library products
- `get_adlibrary_product_detail` — Get Meta Ad Library product detail

### TikTok Shop
- `search_tiktok_products` — Search TikTok Shop products by sales, GMV, price, trends
- `get_tiktok_product_detail` — Get TikTok Shop product detail
- `search_tiktok_shops` — Search TikTok Shop stores
- `get_tiktok_shop_detail` — Get TikTok Shop store detail

### Advertisers & Stores
- `search_advertisers` — Search advertiser leaderboard
- `get_advertiser_detail` — Get advertiser detail
- `search_stores` — Search store ranking list
- `get_store_detail` — Get store detail by ID

### Store Analysis (13 tools)
- `get_store_competition` — Competition analysis
- `get_store_data_analysis` — All-platform data analysis
- `get_store_play_cost` — Play cost statistics
- `get_store_region_analysis` — Regional ad distribution
- `get_store_ad_copy_analysis` — TikTok ad copy analysis
- `get_store_ad_schedule` — Ad campaign schedule
- `get_store_product_analysis` — Product analysis
- `get_store_rank_data` — Traffic ranking data
- `get_store_ad_trend` — Meta Ad Library ad trend
- `get_store_delivery_analysis` — Meta Ad Library delivery analysis
- `get_store_longest_run_ads` — Longest-running ad content
- `get_store_most_used_ads` — Most-used ad content
- `get_store_fb_pages` — Facebook advertiser pages

### Meta Ad Library
- `search_lib_ads` — Search Meta Ad Library ads
- `get_lib_ad_detail` — Get ad detail by ID

### Rankings
- `get_product_ranking` — Ad product ranking
- `get_new_product_ranking` — New product ranking
- `get_app_ranking` — Top apps ranking
- `get_new_app_ranking` — New apps ranking
- `get_app_dev_ranking` — App developers ranking

### Apps
- `search_apps` — Search apps on TikTok/Facebook
- `get_app_detail` — Get app detail
- `search_app_developers` — Search app developers
- `get_app_developer_detail` — Get developer detail

### Natural Traffic
- `search_natural_videos` — Search TikTok natural traffic videos

### Ad Monitor (20 tools)
- `search_fb_advertisers` — Search Facebook advertisers for monitoring
- `create_monitor_task` — Create monitoring task
- `list_monitor_tasks` — List monitoring tasks
- `get_monitor_task_detail` — Task details
- `cancel_monitor_task` — Cancel task
- `get_monitor_board` — Dashboard overview
- `set_monitor_task_group` — Assign task to group
- `get_monitor_realtime_overview` — Real-time overview
- `get_monitor_daily_overview` — Daily overview
- `get_monitor_landing_pages_overview` — Landing pages overview
- `get_monitor_latest_products` — Latest products
- `get_monitor_product_list` — Product list
- `get_monitor_landing_page_list` — Landing page list
- `get_monitor_ad_count_stats` — Ad count statistics
- `get_monitor_deep_analysis` — Deep campaign analysis
- `get_monitor_most_used_copy` — Most-used ad copy
- `get_monitor_longest_run_copy` — Longest-running ad copy
- `get_monitor_ad_list` — Ad list
- `get_monitor_ad_detail` — Ad detail
- `get_monitor_product_stats` — Product statistics

### Monitor Groups & Notifications
- `create_monitor_group` — Create group
- `list_monitor_groups` — List groups
- `update_monitor_group` — Update group
- `delete_monitor_group` — Delete group
- `get_monitor_notifications` — Get notification settings
- `save_monitor_notifications` — Save notification settings

### AI Image Search (8 tools)
- `ai_search_submit_image` — Submit image for visual search
- `ai_search_image_status` — Check processing status
- `ai_search_image_summary` — Get result summary
- `ai_search_image_ads` — Search similar ads
- `ai_search_image_products` — Search similar products
- `ai_search_image_stores` — Search similar stores
- `ai_search_image_tiktok_products` — Search similar TikTok products
- `ai_search_image_tiktok_shops` — Search similar TikTok shops

## Usage Examples

- "Search for trending TikTok ads about phone cases in the US"
- "Find Shopify products with over 100k views in the last 30 days"
- "Show me the top advertisers on Facebook this week"
- "Get store competition analysis for store ID c2d5b2547218a"
- "Create a monitor task for advertiser XYZ"
- "Search TikTok Shop products with rising sales in beauty category"

## Credits

Each API call consumes credits from your PipiAds account:
- **List/Search**: 1 credit per result returned
- **Detail**: 1 credit per request (free if queried within 3 days)
