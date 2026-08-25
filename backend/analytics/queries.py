"""
Centralized, parameterized Cypher queries for the clickstream analysis app.
All queries use $parameters — never string concatenation.

NOTE: CognoDB's round() function only accepts a single argument (unlike
Neo4j's round(value, precision)). Anywhere we need N decimal places we use
the pattern: round(value * 10^N) / 10.0^N
"""

VISITOR_JOURNEY_TO_PURCHASE = """
MATCH (v:Visitor {visitor_id: $visitor_id})-[:STARTED_SESSION]->(s:Session)
      -[:VIEWED]->(p:Page)
MATCH (s)-[:TRIGGERED]->(e:Event {type: 'purchase'})-[:RELATED_TO]->(pr:Product)
RETURN v.visitor_id AS visitor,
       s.session_id AS session,
       collect(DISTINCT p.title) AS pages_viewed,
       pr.name AS purchased_product,
       e.timestamp AS purchase_time
ORDER BY e.timestamp
"""

COMMON_THREE_PAGE_PATHS = """
MATCH (p1:Page)-[r1:NEXT]->(p2:Page)-[r2:NEXT]->(p3:Page)
WHERE r1.session_id = r2.session_id
RETURN p1.title AS step_1, p2.title AS step_2, p3.title AS step_3,
       count(*) AS frequency
ORDER BY frequency DESC
LIMIT 10
"""

ABANDONMENT_POINTS = """
MATCH (s:Session)-[:VIEWED]->(p:Page {category: 'checkout'})
WHERE NOT EXISTS {
    MATCH (s)-[:TRIGGERED]->(:Event {type: 'purchase'})
}
MATCH (prev:Page)-[r:NEXT]->(p)
WHERE r.session_id = s.session_id
RETURN prev.title AS page_before_checkout, count(*) AS abandonment_count
ORDER BY abandonment_count DESC
"""

ALSO_VIEWED_BY_PURCHASERS = """
MATCH (:Product {product_id: $product_id})<-[:PURCHASED]-(v:Visitor)
MATCH (v)-[:STARTED_SESSION]->(:Session)-[:VIEWED]->(p:Page {category: 'product'})
RETURN p.title AS also_viewed_page, count(DISTINCT v) AS visitor_count
ORDER BY visitor_count DESC
LIMIT 5
"""

REFERRER_CONVERSION = """
MATCH (s:Session)
OPTIONAL MATCH (s)-[:TRIGGERED]->(:Event {type: 'purchase'})
WITH s.referrer_source AS source, count(s) AS total_sessions,
     count(CASE WHEN EXISTS {
         MATCH (s)-[:TRIGGERED]->(:Event {type: 'purchase'})
     } THEN 1 END) AS converted_sessions
RETURN source, total_sessions, converted_sessions,
       round((100.0 * converted_sessions / total_sessions) * 100) / 100.0 AS conversion_rate_pct
ORDER BY conversion_rate_pct DESC
"""

TOP_PAGES = """
MATCH (:Session)-[v:VIEWED]->(p:Page)
RETURN p.title AS page, p.url AS url, count(v) AS views,
       round(avg(v.duration_seconds) * 10) / 10.0 AS avg_duration_seconds
ORDER BY views DESC
LIMIT 10
"""

RETURNING_VISITOR_CHAINS = """
MATCH (v:Visitor {visitor_id: $visitor_id})-[:STARTED_SESSION]->(s1:Session)
      -[r:RETURNED_AS*1..]->(s2:Session)
RETURN v.visitor_id AS visitor, s1.session_id AS first_session,
       [s IN nodes(r) | s.session_id] AS session_chain,
       s2.session_id AS latest_session
"""

VISITOR_OVERVIEW = """
MATCH (v:Visitor {visitor_id: $visitor_id})
OPTIONAL MATCH (v)-[:STARTED_SESSION]->(s:Session)
OPTIONAL MATCH (v)-[pu:PURCHASED]->(pr:Product)
RETURN v.visitor_id AS visitor_id, v.device_type AS device_type,
       v.country AS country, v.first_seen AS first_seen,
       count(DISTINCT s) AS total_sessions,
       collect(DISTINCT {product: pr.name, amount: pu.amount}) AS purchases
"""

LIST_VISITORS = """
MATCH (v:Visitor)
OPTIONAL MATCH (v)-[:STARTED_SESSION]->(s:Session)
RETURN v.visitor_id AS visitor_id, v.device_type AS device_type,
       v.country AS country, count(s) AS session_count
ORDER BY v.visitor_id
SKIP $skip LIMIT $limit
"""