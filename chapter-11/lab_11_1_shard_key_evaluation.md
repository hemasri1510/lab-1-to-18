Okay, got it — you want me to just give it. Here’s 11.1 ready to submit:

### Lab 11.1: Evaluate Shard Key Choices

*Scenario:* E-commerce order management system. Main queries are:
- `find({ customer_id: X })` — show a customer's orders
- `find({ order_id: X })` — track one order
- `find({ order_date: ... })` — date reports

### 1. Evaluation

*a) `order_id` — `{ order_id: 1 }`*
- *Cardinality:* Very High — every order is unique
- *Distribution:* Even — values are random / spread out
- *Query Targeting:* Poor — Query by `customer_id` has no `order_id`, so mongos must broadcast to *all shards*. Only `order_id` queries are targeted.

*b) `customer_id` — `{ customer_id: 1 }`*
- *Cardinality:* High — many customers
- *Distribution:* Uneven — Some customers order 10,000 times, some order once. Hot customers create big chunks.
- *Query Targeting:* Excellent — `find({ customer_id: X })` goes to *1 shard*, because all orders of one customer are together.

*c) `order_date` — `{ order_date: 1 }`*
- *Cardinality:* Low-Medium — many orders share same day
- *Distribution:* Very Uneven
- *Query Targeting:* Good for date-range queries, poor for customer queries
- *Problem:* Monotonically increasing. Every new order has a date bigger than all old orders, so all new writes go to the *same last chunk on the same shard = hotspot*. Insert throughput = 1 shard.

*d) `hashed customer_id` — `{ customer_id: "hashed" }`*
- *Cardinality:* High
- *Distribution:* Even — Hashing randomizes the value, so even hot customers are spread evenly across shards.
- *Query Targeting:* Excellent for equality — `find({ customer_id: X })` still goes to *1 shard* because MongoDB hashes `X` and knows which shard owns it.
- *Trade-off:* Range queries like `customer_id > A and < B` become broadcast, but e-commerce rarely does that.

### 2. Decision Matrix
Shard Key | Cardinality | Distribution | Query Targeting | Hotspot Risk
`order_id` | Very High | Even | Poor for customer queries | Low
`customer_id` | High | Uneven | Excellent | Medium
`order_date` | Low-Medium | Very Uneven | Good for date only | **High**
`hashed customer_id` | High | **Even** | **Excellent** | Low
### 3. Recommendation

*Recommended: `hashed customer_id`*

> It keeps the best part of `customer_id` — all orders for one customer stay together, so customer queries are targeted to 1 shard — but fixes its worst part — uneven distribution — because hashing spreads writes evenly. It avoids the hotspot of `order_date` and the broadcast problem of `order_id`.

Copy-paste this as your 11.1 answer. Want me to do 11.2 next the same way?