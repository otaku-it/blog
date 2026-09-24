POSTS = [
    {
        "id": "react-server-components",
        "title": "从零理解 React Server Components",
        "excerpt": "RSC 不只是一次渲染策略升级，它重新定义了组件、数据与服务端之间的边界。",
        "date": "2026-09-18",
        "category": "前端工程",
        "tags": ["React", "Next.js", "架构"],
        "views": 8600,
        "read_time": "12 分钟",
        "content": """## 01. 先建立正确的心智模型

React Server Components 不是 SSR 的新名字。它让一部分组件只在服务端执行，并且不会进入客户端 JavaScript bundle。

> 关键不是消灭客户端，而是让组件运行在最合适的位置。

## 02. 边界：什么应该留在客户端

如果组件需要 `useState`、`useEffect` 或浏览器 API，它就属于客户端边界。

```tsx
export default async function ArticlesPage() {
  const articles = await db.article.findMany()
  return articles.map(article => (
    <ArticleCard key={article.id} article={article} />
  ))
}
```

## 03. 组合，而不是全量迁移

从页面顶层向下识别交互边界，将搜索框、收藏按钮等小型交互岛保留为客户端组件。

## 04. 数据流与缓存策略

数据请求靠近消费数据的组件，但仍要明确静态内容、周期更新和请求级动态数据的缓存方式。

## 05. 三个常见误区

- RSC 不会自动让所有应用变快。
- 对外服务的 API 仍然有存在价值。
- 客户端状态没有过时，只是边界需要缩小。

## 06. 总结

把非交互渲染留在服务端，把必要交互留给浏览器，可以得到更清晰的边界和更少的客户端代码。""",
    },
    {"id":"typescript-patterns","title":"TypeScript 类型体操之后：真正实用的 8 个模式","excerpt":"从领域建模、API 边界和表单状态出发，让类型系统真正降低维护成本。","date":"2026-09-12","category":"编程语言","tags":["TypeScript","工程化"],"views":5200,"read_time":"9 分钟"},
    {"id":"ai-coding-workflow","title":"AI 编程时代，我如何重构个人开发工作流","excerpt":"从需求澄清、上下文管理到代码审查，一套可重复的人机协作开发流程。","date":"2026-09-05","category":"AI 实践","tags":["AI","效率","工作流"],"views":12100,"read_time":"15 分钟"},
    {"id":"web-performance","title":"Web 性能优化：从指标到用户体验","excerpt":"以 Core Web Vitals 为入口，建立从监控、诊断到优化的完整性能闭环。","date":"2026-08-27","category":"前端工程","tags":["性能","Web","监控"],"views":4700,"read_time":"11 分钟"},
    {"id":"node-observability","title":"Node.js 服务可观测性实践指南","excerpt":"日志、指标和链路追踪如何协同？从埋点到告警建立完整的工程闭环。","date":"2026-08-19","category":"后端架构","tags":["Node.js","可观测性","DevOps"],"views":3900,"read_time":"13 分钟"},
    {"id":"css-design-system","title":"用 CSS Variables 构建可扩展设计系统","excerpt":"从语义化 token、明暗主题到组件变体，构建设计与工程共享的基础设施。","date":"2026-08-08","category":"设计工程","tags":["CSS","设计系统","前端"],"views":6300,"read_time":"10 分钟"},
    {"id":"postgres-index","title":"PostgreSQL 索引不是越多越好","excerpt":"理解 B-Tree、GIN 和组合索引的适用边界，避免加索引式优化。","date":"2026-07-30","category":"后端架构","tags":["PostgreSQL","数据库","性能"],"views":7800,"read_time":"14 分钟"},
    {"id":"docker-small-image","title":"把 Docker 镜像从 1.2GB 优化到 86MB","excerpt":"多阶段构建、依赖裁剪、缓存策略与安全扫描的容器镜像瘦身实录。","date":"2026-07-21","category":"DevOps","tags":["Docker","DevOps","性能"],"views":9400,"read_time":"8 分钟"},
    {"id":"micro-frontend","title":"微前端落地两年后的复盘","excerpt":"从组织边界、运行时隔离到版本治理，分享不加滤镜的真实经验。","date":"2026-07-13","category":"前端工程","tags":["微前端","架构","团队"],"views":5600,"read_time":"16 分钟"},
    {"id":"go-concurrency","title":"Go 并发编程中的 6 个常见陷阱","excerpt":"goroutine 泄漏、channel 死锁和数据竞争的根源与修复方式。","date":"2026-07-02","category":"编程语言","tags":["Go","并发","后端"],"views":4200,"read_time":"9 分钟"},
    {"id":"api-design","title":"写给前端工程师的 API 设计指南","excerpt":"资源建模、错误结构、分页、幂等与版本演进中的关键决策。","date":"2026-06-24","category":"后端架构","tags":["API","架构","REST"],"views":6900,"read_time":"12 分钟"},
    {"id":"testing-pyramid","title":"重新思考前端测试金字塔","excerpt":"从反馈速度和维护成本出发，重新分配单测、集成测试与 E2E。","date":"2026-06-15","category":"前端工程","tags":["测试","前端","工程化"],"views":3500,"read_time":"10 分钟"},
]

DEFAULT_CONTENT = """## 为什么值得讨论

从真实服务的故障复盘出发，梳理数据模型、接口边界和可观测性建设，让文章内容可以直接落到工程实践中。

## 实践建议

- 从真实问题出发，而不是从工具出发。
- 保持边界清晰，让系统可以渐进演化。
- 用可观测数据验证优化是否有效。

```python
def build_better_software(problem, feedback):
    return iterate(problem, feedback)
```

## 总结

好的技术方案不是最复杂的方案，而是在当前约束下最清晰、最可靠的方案。"""

COMMENTS = {
    "react-server-components": [
        {"id": 1, "name": "Ming", "content": "组合而不是全量迁移，这点很重要。", "created_at": "2 天前"},
        {"id": 2, "name": "Yuki Chen", "content": "希望后续补充缓存失效策略实战。", "created_at": "5 天前"},
    ]
}

for post in POSTS:
    post.setdefault("content", DEFAULT_CONTENT)
