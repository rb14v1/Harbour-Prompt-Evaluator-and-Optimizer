from typing import Dict, Any, List


class ImproverAgent:
    """Department-specific prompt rewriting - complete rewrites, no appending."""

    def __init__(self):
        self.name = "Improver Agent"

    def improve(
        self,
        original_prompt: str,
        analysis: Dict[str, Any],
        validation: Dict[str, Any],
        scoring: Dict[str, Any],
        iteration: int = 1,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Completely rewrite prompt based on department and expertise."""
        if metadata is None:
            metadata = {}
        return self._department_aware_rewrite(original_prompt, validation, scoring, iteration, metadata)

    def _department_aware_rewrite(
        self, original_prompt: str, validation: Dict[str, Any], scoring: Dict[str, Any], iteration: int, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rewrite from scratch with department-specific structure."""

        if not original_prompt:
            return {"improved_prompt": original_prompt, "changes_made": [], "dimensions_addressed": [], "intent_preserved": True, "iteration": iteration, "reasoning": "No content"}

        department = metadata.get('user_role', 'Software')
        expertise = metadata.get('expertise_level', 'Intermediate')
        context = metadata.get('context', 'Work')

        # Extract core intent and topics
        intent = original_prompt.strip()[:150]
        topics = self._extract_keywords(original_prompt)

        # Generate department-specific rewrite
        improved_prompt = self._generate_department_prompt(
            department=department,
            original_prompt=original_prompt,
            intent=intent,
            topics=topics,
            expertise=expertise,
            context=context
        )

        improvements = [f"Rewritten for {department} department with {expertise.lower()} expertise level"]
        dims_addressed = self._get_dimensions_addressed(scoring)

        return {
            "improved_prompt": improved_prompt,
            "changes_made": improvements,
            "dimensions_addressed": dims_addressed if dims_addressed else ["general"],
            "intent_preserved": True,
            "iteration": iteration,
            "reasoning": f"Iteration {iteration}: Complete rewrite for {department} ({expertise})"
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key topics from text."""
        words = text.lower().split()
        stopwords = {"a", "an", "the", "is", "are", "for", "with", "and", "or", "to", "in", "on", "at", "by", "from"}
        keywords = [w.strip('.,!?;:') for w in words if w not in stopwords and len(w) > 4]
        return list(dict.fromkeys(keywords))[:5]

    def _get_dimensions_addressed(self, scoring: Dict[str, Any]) -> List[str]:
        """Get dimensions that were addressed."""
        dims = []
        low_dims = scoring.get("low_scoring_dimensions", []) if scoring else []
        if low_dims:
            dims.extend(low_dims[:4])
        if not dims:
            dims = ["clarity", "specificity"]
        return dims

    def _generate_department_prompt(self, department: str, original_prompt: str, intent: str, topics: List[str], expertise: str, context: str) -> str:
        """Generate completely new prompt for specific department."""

        handlers = {
            "Software": self._software_prompt,
            "Communication": self._communication_prompt,
            "Design": self._design_prompt,
            "Engineering": self._engineering_prompt,
            "Finance": self._finance_prompt,
            "Human Resources": self._hr_prompt,
            "Learning and Development": self._learning_prompt,
            "Marketing": self._marketing_prompt,
            "Product Management": self._product_prompt,
            "Support": self._support_prompt,
            "Business Analysis": self._business_analysis_prompt,
        }

        handler = handlers.get(department, self._default_prompt)
        return handler(intent, topics, expertise, context)

    def _software_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Develop a software solution for: {intent}

Requirements & Specifications:
- Core functionality: Implement primary features to address the objective
- Architecture: Design scalable, maintainable system architecture
- Technology stack: Specify programming languages, frameworks, and libraries
- Database design: Define schema, relationships, and optimization strategies
- API contracts: Document all endpoints with request/response formats
- Error handling: Comprehensive exception handling and logging
- Performance: Optimization targets and benchmarks
- Security: Authentication, authorization, data protection measures

Implementation Approach:
- Code quality: Follow established coding standards and best practices
- Testing: Unit tests (target {80 if expertise in ['Advanced', 'Expert'] else 70}% coverage)
- Documentation: Code comments, API documentation, deployment guides
- Version control: Git workflow with clear commit messages
- CI/CD integration: Automated testing and deployment pipeline

{"Advanced Considerations:" if expertise in ["Advanced", "Expert"] else "Additional Notes:"}
- {"Scalability patterns, microservices, cloud deployment" if expertise in ["Advanced", "Expert"] else "Deployment instructions, maintenance guidelines"}
- Performance optimization strategies
- Monitoring and observability requirements
- Technical debt management

Deliverables:
- Functional codebase with working features
- Comprehensive documentation
- Test suite with high coverage
- Deployment and setup instructions"""

    def _communication_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Create a communication strategy for: {intent}

Communication Objectives:
- Primary message: Core idea to communicate
- Key stakeholders: Identify target audiences
- Channel selection: Choose appropriate communication channels
- Message framework: Develop clear, compelling messaging

Content Development:
- Main talking points: {', '.join(topics) if topics else 'Core messages to emphasize'}
- Tone and style: {"Professional and authoritative" if context == "Client Presentation" else "Clear and accessible"}
- Content structure: Introduction, body (3-5 key points), conclusion
- Call to action: Clear next steps or desired outcome

Audience Engagement:
- Audience analysis: Demographics, knowledge level, concerns
- Engagement tactics: Questions, discussions, interactive elements
- Visual support: Recommended visual aids or supporting materials
- Feedback mechanisms: How to gather and respond to audience feedback

Delivery Approach:
- {"Presentation structure with speaker notes" if "Presentation" in intent or "presentation" in intent.lower() else "Communication format and timing"}
- Key messages to emphasize at each stage
- Handling objections and difficult questions
- Following up after communication

Success Metrics:
- How to measure communication effectiveness
- Audience understanding and retention targets
- Action/behavior change indicators"""

    def _design_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Design solution for: {intent}

Design Brief:
- Problem statement: What needs to be solved
- User research: Target users, needs, pain points
- Design objectives: {', '.join(topics) if topics else 'Aesthetic, functional, usability goals'}
- Constraints: Budget, timeline, technical limitations

Design Process:
- Discovery: Analyze requirements and existing solutions
- Ideation: Generate multiple design concepts
- Wireframing: Low-fidelity layouts and information architecture
- Prototyping: Interactive mockups for user testing
- {"Detailed specifications and design systems" if expertise in ["Advanced", "Expert"] else "Visual refinement and finalization"}

Visual Design Standards:
- Color palette: Primary, secondary, accent colors with rationale
- Typography: Font selections, hierarchy, sizing rules
- Component library: Reusable UI elements and patterns
- Accessibility: WCAG compliance (AA minimum)
- Responsive design: Desktop, tablet, mobile breakpoints

User Experience:
- User flows: Step-by-step interaction paths
- Navigation structure: Information hierarchy and pathways
- Interaction patterns: Feedback, loading states, error handling
- Usability testing: Methods and success criteria

Deliverables:
- Design system documentation
- High-fidelity mockups and prototypes
- Handoff specifications for developers
- Design rationale and decision documentation"""

    def _engineering_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Engineering project for: {intent}

Project Definition:
- Scope: {intent}
- Key objectives: {', '.join(topics) if topics else 'Performance, reliability, efficiency targets'}
- Success criteria: Measurable outcomes
- Timeline and milestones: Phase breakdown

Technical Specifications:
- Design specifications: Detailed technical approach
- Materials and components: Selection and sourcing
- System requirements: Power, computing, environmental conditions
- Safety requirements: Regulatory compliance, safety margins
- Performance benchmarks: Speed, accuracy, efficiency targets

Development Phases:
1. Planning: Feasibility analysis, resource allocation
2. Design: Detailed CAD/technical drawings, simulations
3. Prototyping: Proof of concept and testing
4. Implementation: Manufacturing or deployment
5. Testing & Validation: Quality assurance, performance verification
6. Deployment: Commissioning and handover

Quality Assurance:
- Testing protocols: {"Comprehensive testing including edge cases" if expertise in ["Advanced", "Expert"] else "Standard quality checks"}
- Documentation: Technical manuals, maintenance guides
- Compliance: Standards adherence (ISO, industry-specific)
- Risk mitigation: Failure analysis, backup systems

Project Deliverables:
- Technical drawings and specifications
- Bill of materials
- Assembly/deployment instructions
- Test and validation reports
- Maintenance and troubleshooting guides"""

    def _finance_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Financial analysis and planning for: {intent}

Financial Objectives:
- Primary goal: {intent}
- Key metrics: {', '.join(topics) if topics else 'Revenue, profitability, ROI, cost savings'}
- Time horizon: Short-term (0-1 year), medium-term (1-3 years), long-term (3+ years)
- Success targets: Specific financial outcomes

Analysis Framework:
- Current state: Baseline financial metrics and KPIs
- Assumptions: Key drivers and variables
- Projections: Revenue forecasts, cost estimations
- Scenarios: Best case, realistic, worst case outcomes
- Sensitivity analysis: Impact of variable changes

Financial Modeling:
- Income statement projections
- Cash flow analysis
- Balance sheet considerations
- Break-even analysis
- {"Monte Carlo simulations for risk assessment" if expertise in ["Advanced", "Expert"] else "Risk and contingency planning"}

Decision Making:
- Cost-benefit analysis
- ROI calculations and payback period
- Comparison with alternatives
- Risk assessment and mitigation
- Recommendation and rationale

Reporting:
- Executive summary with key findings
- Detailed financial statements and schedules
- Supporting assumptions and methodology
- Visual charts and dashboards
- Implementation roadmap with milestones"""

    def _hr_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Human Resources initiative for: {intent}

Initiative Overview:
- Objective: {intent}
- Focus areas: {', '.join(topics) if topics else 'Recruitment, retention, engagement, compliance'}
- Target audience: Employees, managers, leadership
- Expected impact: Organizational and employee benefits

Strategic Approach:
- Current state assessment: Gaps, challenges, opportunities
- Best practices: Industry standards and benchmarks
- Implementation strategy: Phased rollout and change management
- Stakeholder engagement: Communication and buy-in plan
- Timeline: Key milestones and deadlines

Program Components:
- Policy and procedure updates
- Training and development requirements
- Technology and systems needed
- Resource allocation and budget
- Performance metrics and success indicators

Execution Plan:
- Detailed action steps
- Responsible parties and accountability
- Communication schedule
- Training delivery approach
- Monitoring and adjustment process

Success Metrics:
- {"Engagement surveys, retention rates, diversity metrics" if expertise in ["Advanced", "Expert"] else "Key performance indicators"}
- Tracking and reporting methodology
- Regular review and optimization
- ROI measurement

Deliverables:
- Program documentation and policies
- Training materials
- Communication templates
- Implementation timeline
- Measurement framework"""

    def _learning_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Learning and Development program for: {intent}

Program Design:
- Learning objectives: What participants will achieve
- Target audience: Skill level, background, learning preferences
- Content focus: {', '.join(topics) if topics else 'Key skills and knowledge areas'}
- Delivery format: Online, in-person, blended, self-paced
- Duration: Total hours, schedule, pacing

Curriculum Structure:
- Modules/units: Logical content breakdown
- Learning progression: Foundation to advanced
- Core topics: Essential knowledge and skills
- Practical applications: Real-world use cases
- Assessment methods: Knowledge checks, projects, certification

Instructional Design:
- Learning activities: Lectures, discussions, hands-on practice
- Interactive elements: Quizzes, simulations, case studies
- {"Advanced pedagogical techniques, adaptive learning" if expertise in ["Advanced", "Expert"] else "Engagement strategies and motivation"}
- Resources: Textbooks, videos, tools, references
- Support mechanisms: Office hours, forums, mentoring

Assessment & Evaluation:
- Pre-assessment: Baseline knowledge evaluation
- Formative assessments: Progress checks throughout
- Summative assessment: Final knowledge verification
- Certification: Credentials and recognition
- Program evaluation: Participant feedback and learning outcomes

Implementation:
- Instructor/facilitator requirements
- Technology platform selection
- Content development timeline
- Pilot testing and refinement
- Full launch and scaling strategy

Deliverables:
- Complete course curriculum
- Instructional materials
- Assessment tools
- Facilitator guides
- Participant resources and certification program"""

    def _marketing_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Marketing campaign for: {intent}

Campaign Strategy:
- Campaign objective: {intent}
- Target audience: Demographics, psychographics, pain points
- Key messages: {', '.join(topics) if topics else 'Value proposition, differentiation, benefits'}
- Campaign duration: Launch date, seasonal considerations
- Budget allocation: Total spend and channel distribution

Market Analysis:
- Competitive landscape: Key competitors and positioning
- Market trends: Relevant industry movements
- Customer insights: Needs, preferences, behaviors
- Market opportunity: Addressable market and growth potential

Campaign Components:
- Channels: Digital (email, social, search, display), traditional, PR
- Content strategy: Blog posts, videos, infographics, social content
- Creative concept: Messaging theme and visual direction
- Campaign timeline: Key dates and deliverables

Digital Strategy:
- Website optimization: Messaging, user experience, conversions
- Social media: Platform selection, content calendar, engagement
- Email marketing: Segmentation, messaging, automation
- Paid advertising: Targeting, bidding strategy, creative variations
- Analytics: Tracking, measurement, optimization

Launch & Execution:
- Pre-launch activities: Teaser content, partner coordination
- Launch strategy: Announcement and visibility plan
- Ongoing optimization: A/B testing, performance monitoring
- Team roles: Responsibilities and accountability
- Timeline: Phases from planning through analysis

Measurement & ROI:
- Success metrics: Reach, engagement, conversions, revenue
- Tracking setup: Analytics, pixels, attribution
- Reporting: Regular performance reviews
- Optimization: Learnings and adjustments
- {"Attribution modeling and ROI optimization" if expertise in ["Advanced", "Expert"] else "Post-campaign analysis and recommendations"}"""

    def _product_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Product strategy for: {intent}

Product Vision:
- Product mission: Core purpose and value
- Problem solved: User pain points addressed
- Target market: Primary users and segments
- Success definition: Goals and key metrics
- Unique value: Differentiation from alternatives

Product Requirements:
- Core features: {', '.join(topics) if topics else 'Essential functionality'}
- User stories: How users will interact
- Use cases: Primary and secondary scenarios
- {"Advanced features and roadmap" if expertise in ["Advanced", "Expert"] else "Future enhancement possibilities"}
- Acceptance criteria: How to verify features work

Product Roadmap:
- Phases: MVP, Phase 1, Phase 2, future
- Feature prioritization: Based on user needs and business value
- Timeline: Realistic delivery estimates
- Dependencies: Technology, resources, partnerships needed
- Milestones: Key release dates and deliverables

Go-to-Market Strategy:
- Launch approach: Soft launch, beta, full launch
- Pricing strategy: Pricing model and justification
- Distribution: How customers access the product
- Marketing: Awareness and demand generation
- Sales: Sales process and enablement

Metrics & Success:
- Key performance indicators: Adoption, usage, revenue
- User feedback: Collection and response mechanisms
- Competitive monitoring: Market and competitor tracking
- {"Advanced analytics and growth optimization" if expertise in ["Advanced", "Expert"] else "Regular review and adjustment process"}

Cross-functional Requirements:
- Engineering: Technical feasibility and timeline
- Design: User experience and interface
- Marketing: Positioning and messaging
- Sales: Enablement and support
- Support: Customer success and issue resolution"""

    def _support_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Customer support program for: {intent}

Support Strategy:
- Support objective: {intent}
- Service level targets: Response time, resolution time, satisfaction goals
- Support channels: Email, chat, phone, social media, ticket system
- Coverage: Hours of operation, languages, timezone considerations
- Support team: Size, skills, training requirements

Support Operations:
- Ticketing system: Configuration and workflow
- Knowledge base: Documentation and self-service resources
- FAQs: Common issues and quick answers
- Escalation procedure: Handling complex issues
- {"Multi-tier support with specialized teams" if expertise in ["Advanced", "Expert"] else "Support processes and procedures"}

Quality & Performance:
- Service level agreements: Response and resolution targets
- Quality metrics: Customer satisfaction, ticket resolution rate
- Performance monitoring: Dashboards and reporting
- Continuous improvement: Issue analysis and process optimization
- Training: Onboarding and skill development

Customer Communication:
- Response templates: Consistent, professional communication
- Issue documentation: Clear problem description and solution
- Feedback collection: Customer satisfaction surveys
- Proactive outreach: Informing customers of issues/updates
- Follow-up: Verification of resolution and prevention

Technology & Tools:
- Support platform: Selection and configuration
- Knowledge management system: Documentation and search
- Integration: CRM, billing, product systems
- Analytics: Performance tracking and insights
- Automation: Chatbots, auto-responses, workflows

Continuous Improvement:
- Issue trend analysis: Common problems and patterns
- Root cause analysis: Addressing underlying issues
- Feature requests: Feedback to product team
- Process refinement: Regular optimization
- Team development: Skill enhancement and career growth"""

    def _business_analysis_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Business analysis for: {intent}

Project Overview:
- Business objective: {intent}
- Current state: Existing processes and systems
- Desired state: Target improvements and outcomes
- Stakeholders: Key decision makers and users
- Timeline: Project schedule and milestones

Requirements Gathering:
- Stakeholder interviews: Understanding needs and constraints
- Process documentation: Current workflows and pain points
- {"Comprehensive requirement analysis with traceability" if expertise in ["Advanced", "Expert"] else "Key requirements identification"}
- Business rules: Rules, policies, and constraints
- Success criteria: How to measure success

Analysis & Recommendations:
- Gap analysis: Difference between current and desired state
- Alternative solutions: Multiple approaches with pros/cons
- Cost-benefit analysis: Financial impact of options
- Risk assessment: Potential obstacles and mitigation
- Recommendation: Preferred approach with rationale

Implementation Planning:
- Solution design: Detailed approach and components
- Resource requirements: People, technology, budget
- Timeline: Phased implementation plan
- Change management: Organizational impact and adoption strategy
- Risk mitigation: Contingency planning

Documentation:
- Business requirements specification
- Use cases and scenarios
- Process flows and diagrams
- {"Detailed specifications and traceability matrix" if expertise in ["Advanced", "Expert"] else "Solution overview and change impact"}
- Implementation guidelines

Metrics & Monitoring:
- Success metrics: How to measure outcome
- KPIs: Performance indicators to track
- Monitoring plan: Ongoing performance tracking
- Optimization: Continuous improvement approach
- Lessons learned: Post-implementation review"""

    def _default_prompt(self, intent: str, topics: List[str], expertise: str, context: str) -> str:
        return f"""Complete the following task: {intent}

Objectives:
- Primary goal: {intent}
- Key focus areas: {', '.join(topics) if topics else 'Comprehensive coverage of all aspects'}
- Target context: {context}
- Expertise level required: {expertise}

Approach:
- Detailed planning and preparation
- Clear execution strategy
- Quality assurance and validation
- Documentation and reporting
- Continuous improvement

Deliverables:
- Complete solution addressing the objective
- Supporting documentation
- Clear communication of results
- Recommendations for future actions

Success Criteria:
- Objective achieved
- High quality output
- Stakeholder satisfaction
- On schedule and within budget"""
