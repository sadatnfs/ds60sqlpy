# Advanced SQL Proficiency - 60 Day Lesson Plan
**Duration:** 2 months | **Frequency:** Daily (1-1.5 hours per session) | **Total Exercises:** 60+

---

## Learning Path Overview

```
Phase 1 (Days 1-15):   Fundamentals & Intermediate Review
Phase 2 (Days 16-30):  Advanced Query Techniques
Phase 3 (Days 31-45):  Performance & Optimization
Phase 4 (Days 46-60):  Complex Real-world Projects
```

---

## Phase 1: Fundamentals & Intermediate SQL Review (Days 1-15)

### Week 1: Core SQL & Joins Mastery

**Day 1: SELECT, WHERE, ORDER BY Review**
- Topics: SELECT clauses, filtering with WHERE, ORDER BY, LIMIT
- Key Focus: Understand query execution order
- Exercise: Write 5 queries using different WHERE conditions and sorting

**Day 2: Aggregate Functions & GROUP BY**
- Topics: COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING
- Key Focus: Aggregation logic and filtering grouped data
- Exercise: Create 3 GROUP BY queries with HAVING clauses

**Day 3: INNER JOIN Deep Dive**
- Topics: INNER JOIN syntax, multiple joins, join conditions
- Key Focus: Query optimization for multiple joins
- Exercise: Write queries joining 3+ tables with various conditions

**Day 4: LEFT, RIGHT, FULL OUTER Joins**
- Topics: Non-inner joins, handling NULLs, join directions
- Key Focus: When to use each join type
- Exercise: Convert INNER JOINs to OUTER JOINs and analyze result differences

**Day 5: CROSS JOIN & Self Joins**
- Topics: Cartesian products, self-joins, alias usage
- Key Focus: Practical use cases for CROSS JOIN and self-joins
- Exercise: Write self-join queries (e.g., employee-manager hierarchy)

**Day 6: UNION, UNION ALL, INTERSECT, EXCEPT**
- Topics: Set operations, combining result sets
- Key Focus: Performance differences between operations
- Exercise: Create queries combining multiple SELECT statements

**Day 7: Review & Mini-Project**
- Exercise: Build a comprehensive report combining joins, aggregates, and set operations
- Benchmark: Should combine 3+ tables, multiple joins, and aggregations

---

### Week 2: Subqueries & Data Manipulation

**Day 8: Scalar & Inline Subqueries**
- Topics: Subqueries in SELECT and WHERE clauses
- Key Focus: When subqueries are better than joins
- Exercise: Convert 5 JOIN queries to subquery equivalents

**Day 9: Correlated Subqueries**
- Topics: Row-by-row processing, EXISTS, IN with subqueries
- Key Focus: Performance implications, when to avoid
- Exercise: Write correlated subqueries for complex filtering

**Day 10: INSERT, UPDATE, DELETE with Subqueries**
- Topics: Data manipulation using subqueries
- Key Focus: Transaction safety, rollback understanding
- Exercise: Insert/update/delete records using subqueries on test data

**Day 11: CASE Statements & Conditional Logic**
- Topics: Simple CASE, searched CASE, CASE in aggregations
- Key Focus: Complex conditional transformations
- Exercise: Transform data using multiple CASE statements

**Day 12: String Functions & Manipulation**
- Topics: SUBSTR, CONCAT, LENGTH, TRIM, UPPER, LOWER, REPLACE
- Key Focus: Data cleaning and standardization
- Exercise: Clean messy data using string functions

**Day 13: Date/Time Functions**
- Topics: Date arithmetic, DATEDIFF, DATE_ADD, EXTRACT, FORMAT
- Key Focus: Timezone handling, date comparisons
- Exercise: Calculate date ranges, age calculations, fiscal year grouping

**Day 14: Numeric & Type Conversion Functions**
- Topics: ROUND, CEIL, FLOOR, CAST, CONVERT, NULL handling
- Key Focus: Type safety and data accuracy
- Exercise: Perform calculations with proper type handling

**Day 15: Phase 1 Project - Complex Report**
- Build a report using: joins, subqueries, CASE statements, string/date functions
- Example: Customer purchase analysis with segmentation and temporal patterns
- Deliverable: Fully commented SQL script with 3+ queries

---

## Phase 2: Advanced Query Techniques (Days 16-30)

### Week 3: Window Functions Part 1

**Day 16: Window Functions Fundamentals**
- Topics: OVER clause, PARTITION BY, ORDER BY, frame definitions
- Key Focus: How window functions differ from GROUP BY
- Exercise: Write 5 queries converting GROUP BY logic to window functions

**Day 17: ROW_NUMBER(), RANK(), DENSE_RANK()**
- Topics: Ranking functions, duplicate handling
- Key Focus: Differences and use cases
- Exercise: Rank customers by purchases, employees by salary within departments

**Day 18: LAG() and LEAD()**
- Topics: Accessing previous/next rows, year-over-year comparison
- Key Focus: Time series analysis
- Exercise: Calculate period-over-period changes, running differences

**Day 19: Running Aggregates with Window Functions**
- Topics: SUM() OVER with frame specifications, moving averages
- Key Focus: Frame syntax: ROWS BETWEEN ... PRECEDING/FOLLOWING
- Exercise: Calculate running totals, moving averages, cumulative sums

**Day 20: FIRST_VALUE() and LAST_VALUE()**
- Topics: Accessing first/last values in window
- Key Focus: Frame specification impact
- Exercise: Compare current value to first/last, calculate deviations

**Day 21: NTILE() and PERCENT_RANK()**
- Topics: Distribution functions, percentile bucketing
- Key Focus: Quantile analysis
- Exercise: Segment customers into quartiles, calculate percentile rankings

**Day 22: Advanced Window Function Scenarios**
- Combine multiple window functions in one query
- Exercise: Multi-level analysis (rank within partition, then across all)

---

### Week 4: CTEs & Advanced Query Patterns

**Day 23: Common Table Expressions (CTEs) Introduction**
- Topics: WITH clause syntax, single CTEs
- Key Focus: Readability vs. subqueries
- Exercise: Rewrite 3 complex subqueries as CTEs

**Day 24: Recursive CTEs**
- Topics: Anchoring, recursion, hierarchy traversal
- Key Focus: Avoiding infinite loops, recursion limits
- Exercise: Build organizational hierarchies, generate sequences

**Day 25: Multiple CTEs & Complex Hierarchies**
- Topics: Multiple WITH clauses, CTE referencing
- Key Focus: Query organization and performance
- Exercise: Build 3-level hierarchies with multiple CTEs

**Day 26: CTEs with Window Functions**
- Topics: Combining CTEs and window functions
- Key Focus: Query optimization strategies
- Exercise: Create complex multi-stage analyses

**Day 27: PIVOT / UNPIVOT (or equivalent)**
- Topics: Cross-tabulation, data reshaping
- Key Focus: Database-specific syntax variations
- Exercise: Create pivoted reports, transpose data

**Day 28: JSON/XML Handling (Database-specific)**
- Topics: JSON_EXTRACT, JSON_ARRAY, XML functions
- Key Focus: Semi-structured data querying
- Exercise: Query nested JSON, extract arrays/objects

**Day 29: Advanced Filtering & Pattern Matching**
- Topics: REGEXP, LIKE patterns, full-text search
- Key Focus: Performance implications of pattern matching
- Exercise: Complex LIKE patterns, regex queries

**Day 30: Phase 2 Project - Multi-stage Analysis**
- Build complex analysis using: CTEs, window functions, recursion
- Example: Customer lifetime value with cohort analysis and predictions
- Deliverable: Multi-CTE query (3-4 stages) with full documentation

---

## Phase 3: Performance & Optimization (Days 31-45)

### Week 5: Indexing & Query Planning

**Day 31: Query Execution Plans**
- Topics: EXPLAIN/ANALYZE, plan interpretation, cost analysis
- Key Focus: Identifying bottlenecks
- Exercise: Analyze 5 queries, predict execution times

**Day 32: Index Fundamentals**
- Topics: B-tree, hash indexes, index types
- Key Focus: When indexes help/hurt
- Exercise: Create indexes for queries, measure performance

**Day 33: Index Optimization Strategies**
- Topics: Composite indexes, covering indexes, partial indexes
- Key Focus: Query rewriting for index usage
- Exercise: Optimize 5 poorly performing queries with indexes

**Day 34: Query Optimization Techniques**
- Topics: JOIN optimization, predicate pushdown, column pruning
- Key Focus: Cost-based optimization
- Exercise: Rewrite 5 queries for better performance

**Day 35: Avoiding Common Performance Pitfalls**
- Topics: Functions in WHERE, correlated subqueries, N+1 queries
- Key Focus: Anti-patterns
- Exercise: Identify and fix 10 slow query anti-patterns

**Day 36: Materialized Views & Caching**
- Topics: Materialized views, query result caching
- Key Focus: Trade-offs between freshness and speed
- Exercise: Design materialized views for reporting layer

**Day 37: Partitioning & Data Sharding**
- Topics: Table partitioning, data distribution strategies
- Key Focus: Large table management
- Exercise: Design partitioning strategy for billion-row table

---

### Week 6: Advanced Topics & Transactions

**Day 38: Transactions & ACID Properties**
- Topics: BEGIN, COMMIT, ROLLBACK, isolation levels
- Key Focus: Consistency and concurrency control
- Exercise: Write transaction scenarios, test isolation levels

**Day 39: Locks & Deadlock Prevention**
- Topics: Row locks, table locks, deadlock detection
- Key Focus: Concurrent modification safety
- Exercise: Simulate deadlocks, implement lock ordering strategies

**Day 40: Analytic Functions - Advanced**
- Topics: RATIO_TO_REPORT, STDDEV, VAR_POP over windows
- Key Focus: Statistical analysis in SQL
- Exercise: Calculate cohort metrics, statistical distributions

**Day 41: Complex Aggregations**
- Topics: FILTER clause, conditional aggregates, string aggregation
- Key Focus: Advanced aggregation patterns
- Exercise: Build multi-metric reports, string concatenation aggregates

**Day 42: Data Quality & Validation**
- Topics: Constraint checking, duplicate detection, null analysis
- Key Focus: Data governance
- Exercise: Write data quality validation queries

**Day 43: Backup & Recovery Scenarios**
- Topics: Backup strategies, point-in-time recovery, archival
- Key Focus: Data protection
- Exercise: Design recovery procedures

**Day 44: Monitoring & Diagnostics**
- Topics: Query logs, slow query analysis, wait events
- Key Focus: Production troubleshooting
- Exercise: Analyze slow query logs, identify issues

**Day 45: Phase 3 Project - Performance Optimization**
- Take existing slow queries, optimize to target performance
- Measure: Query time reduction >70%, resource usage improvement
- Deliverable: Before/after analysis, optimization documentation

---

## Phase 4: Complex Real-world Projects (Days 46-60)

### Week 7-8: Capstone Projects

**Day 46-48: Project 1 - E-commerce Analytics**
- Requirements:
  - Customer segmentation by lifetime value
  - Cohort retention analysis
  - Product affinity analysis
  - Attribution analysis (first touch, last touch, multi-touch)
- Advanced Techniques: CTEs, window functions, recursion
- Deliverable: 5+ queries, performance benchmarks

**Day 49-51: Project 2 - Financial/Operational Analysis**
- Requirements:
  - Revenue forecasting with time-series patterns
  - Expense categorization and variance analysis
  - Cash flow projections
  - Budget vs. actual analysis with rolling periods
- Advanced Techniques: Advanced window functions, complex date logic
- Deliverable: Dashboard query suite, optimization notes

**Day 52-54: Project 3 - Data Warehouse Design**
- Requirements:
  - Design fact and dimension tables
  - Implement slowly changing dimensions (SCD)
  - Create aggregation tables
  - Build data quality monitoring
- Advanced Techniques: Complex joins, aggregations, partitioning
- Deliverable: Schema design, ETL queries

**Day 55-57: Project 4 - Complex Business Intelligence**
- Requirements:
  - Multi-dimensional analysis (drill-down capability)
  - Ranking and percentile reporting
  - Trend analysis and anomaly detection
  - Forecast accuracy measurement
- Advanced Techniques: Recursion, complex aggregations, statistical functions
- Deliverable: Query framework, documentation

**Day 58-60: Final Capstone - Integrated Data Challenge**
- Build a complete analytics solution combining:
  - Real-world messy data (handle quality issues)
  - Complex business logic (multi-level calculations)
  - Performance requirements (optimize for 100M+ rows)
  - Multiple stakeholder queries (reports, dashboards, ad-hoc)
- Success Criteria:
  - All queries execute <10s on large dataset
  - Complete data quality validation
  - Clear documentation for maintenance
  - Ability to explain optimization decisions

---

## Daily Exercise Structure

Each day should follow this pattern:

```
1. Conceptual Learning (15-20 min)
   - Read documentation
   - Watch tutorial or review examples
   
2. Guided Practice (20-30 min)
   - Follow along with examples
   - Reproduce demonstrated queries
   
3. Independent Exercises (20-30 min)
   - Solve 3-5 practice problems
   - Apply to new datasets
   
4. Review & Reflection (10 min)
   - Write brief notes on learnings
   - Document gotchas/insights
```

---

## Resources Recommended

### Documentation
- PostgreSQL/MySQL/SQL Server Official Docs (depending on your database)
- Mode Analytics SQL Tutorial
- W3Schools SQL Reference

### Practice Platforms
- LeetCode Database Problems
- HackerRank SQL Challenges
- DataCamp SQL Courses
- StrataScratch SQL Interview Questions

### Tools
- DBeaver or pgAdmin (database client)
- Explain Plan Analyzer (database-specific)
- Performance monitoring tools

---

## Success Metrics

By Day 60, you should be able to:

✓ Write complex multi-join queries with 5+ tables  
✓ Optimize slow queries using EXPLAIN and indexes  
✓ Master window functions for advanced analytics  
✓ Use CTEs for clean, maintainable code  
✓ Handle recursive queries and hierarchical data  
✓ Understand transactions and concurrency control  
✓ Design performant queries on billion-row datasets  
✓ Implement real-world business logic in SQL  
✓ Debug and troubleshoot production queries  
✓ Architect data solutions from requirements to optimization  

---

## Checkpoint Tests

- **Day 15:** Intermediate SQL Assessment (should score 80%+)
- **Day 30:** Advanced Queries Assessment (should score 75%+)
- **Day 45:** Performance Optimization Assessment (should score 70%+)
- **Day 60:** Capstone Project Review (successful execution)

---

## Tips for Success

1. **Database Choice:** Pick one database (PostgreSQL recommended for learning - most feature-rich free option)
2. **Real Data:** Use real or realistic datasets from Day 1
3. **Document Everything:** Keep notes on patterns and gotchas
4. **Test Performance:** Always check EXPLAIN on queries after Day 31
5. **Code Review:** Compare your queries to others' solutions
6. **Build Projects:** Don't just do exercises - build complete solutions
7. **Join Communities:** Participate in SQL communities for feedback
8. **Track Progress:** Keep a log of what you've learned each week

