# Betting System Microservices

## Services Overview

1. **Line Provider** - Manages sports events
2. **Bet Maker** - Handles betting operations

## Quick Start

```bash
docker-compose up -d


Services will be available at:

Line Provider: http://localhost:8000

Bet Maker: http://localhost:8001


Key Endpoints
Line Provider
POST /api/v1/events/events-list - Get events list
Сортировка и фильрация в body 
{
page_number: int = 1
    page_size: int = 10
    sort: Asc or Desc
    filters: field: {
        type_field : EVENT_ID = "event_id"
        COEFFICIENT = "coefficient"
        DEADLINE = "deadline"
        }
   }
PUT /api/v1/events/create
PATCH /api/v1/events/{event_id}
POST /api/v1/events/{event_id}/finish - Finish event

Bet Maker
POST /api/v1/bets - Create bet

GET /api/v1/bets - List all bets

POST /api/v1/bets/callback - Status update callback