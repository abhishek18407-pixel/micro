import json
import os

DEALS = [
    {
        "id": "deal-1",
        "company": "Northwind Logistics",
        "value": 180000,
        "outcome": None,
        "calls": [
            {
                "call_no": 1,
                "date": "2026-10-14",
                "participants": ["Alex Rivera", "David Chen", "Marcus Vance"],
                "transcript": (
                    "Marcus Vance: Alex, thanks for jumping on. We've seen our AWS bills spiral over the "
                    "past three quarters across our 14 regional distribution hubs. Our logistics dispatch "
                    "relies on custom SAP ERP modules that generate massive telemetry spikes. David joined "
                    "us to evaluate whether your platform can handle that kind of high-throughput data stream.\n\n"
                    "Alex Rivera: Marcus, David, great to meet you both. Yes, our platform is built specifically "
                    "for distributed enterprises dealing with unpredictable infrastructure spikes. We ingest billing, "
                    "container, and instance metrics in near-real-time to pinpoint orphaned resources and idle clusters.\n\n"
                    "David Chen: That sounds promising, Alex, but we've been burned before. Our previous logistics "
                    "analytics vendor failed completely because their webhooks suffered from six-hour notification lags, "
                    "which meant we detected expensive idle capacity only after billing cycles closed. If we're going "
                    "to replace them, we need sub-second query latency and seamless ingestion from our Kafka pipelines.\n\n"
                    "Alex Rivera: Understood, David. We use event-driven streaming adapters that give you real-time "
                    "visibility into Kubernetes pods and custom SAP instances within seconds, not hours. I promise I "
                    "will send over our technical architecture overview and SAP ingestion specs by end of day so you "
                    "can inspect the data flow.\n\n"
                    "David Chen: Send that over. If the ingestion architecture looks solid, I'll bring our lead architect "
                    "Elena into a deep-dive call next week."
                ),
            },
            {
                "call_no": 2,
                "date": "2026-10-22",
                "participants": ["Alex Rivera", "David Chen", "Elena Rostova"],
                "transcript": (
                    "David Chen: Welcome back, Alex. Elena reviewed the architecture whitepaper you sent over. "
                    "She's got some hard technical questions around latency and our legacy SAP sync.\n\n"
                    "Elena Rostova: Hi Alex. My primary concern is the compute overhead on our Kafka brokers. We run "
                    "14 distribution centers with continuous telemetry streams. How does your collector agent handle "
                    "schema drift without dropping connection packets or spiking API latency?\n\n"
                    "Alex Rivera: Elena, our lightweight agent executes local deduplication and compresses telemetry "
                    "payloads before transmitting to our ingestion gateway. In similar supply chain setups, CPU "
                    "utilization on client brokers remained under 1.5% with sub-second dashboard refreshes.\n\n"
                    "Elena Rostova: That's lower than I expected. But what about the complexity of the initial mapping? "
                    "Our SAP tables are heavily customized for freight dispatch.\n\n"
                    "David Chen: That's my biggest hesitation too, Alex. Integration with our existing ERP timeline "
                    "and complexity could derail our engineering sprint schedule. We can't afford a four-month integration slog.\n\n"
                    "Alex Rivera: I completely understand, David. To put your mind at ease, I promise to provide custom ERP "
                    "benchmark data and security audit results by November 20th so your team can evaluate sync overhead "
                    "and verify data isolation before making any commitment.\n\n"
                    "David Chen: Fair enough. If those benchmarks prove clean, I'll set up an executive review with our "
                    "CFO, Sarah Jenkins."
                ),
            },
            {
                "call_no": 3,
                "date": "2026-11-03",
                "participants": ["Alex Rivera", "David Chen", "Sarah Jenkins"],
                "transcript": (
                    "Sarah Jenkins: Alex, David has spoken highly of your platform's technical capabilities, but my job as "
                    "CFO is to protect our margins. The $180,000 annual licensing fee you quoted is a substantial line item, "
                    "especially when freight volumes have fluctuated this quarter. Our quarterly budget limits are extremely tight.\n\n"
                    "Alex Rivera: Sarah, I appreciate you being direct. When looking at $180,000, our enterprise logistics customers "
                    "typically uncover 25% to 30% in annualized cloud waste within their first 60 days. In Northwind's case, with 14 "
                    "distribution centers, that translates to over $350,000 in projected cloud savings.\n\n"
                    "Sarah Jenkins: Projections on paper are fine, Alex, but upfront implementation fees relative to quarterly "
                    "budget limits represent real financial risk. We need a guaranteed payback period inside 90 days. Furthermore, "
                    "any software contract over $100,000 requires full board approval before the end of our fiscal quarter in December.\n\n"
                    "David Chen: Sarah, from an engineering standpoint, our idle container burn is costing us nearly $35,000 every month "
                    "right now. Delaying adoption also carries a hefty cost.\n\n"
                    "Sarah Jenkins: I hear you, David, but until I see a financial risk mitigation model and hard ROI milestones, I "
                    "cannot authorize signing an upfront annual commitment. Alex, send us a structured payback schedule.\n\n"
                    "Alex Rivera: Understood, Sarah. I will model out a conservative ROI ramp tailored directly to your 14 distribution centers."
                ),
            },
            {
                "call_no": 4,
                "date": "2026-11-12",
                "participants": ["Alex Rivera", "David Chen", "Tom Bradley"],
                "transcript": (
                    "Tom Bradley: Alex, Sarah asked procurement to step into this evaluation. Before we can even discuss contract "
                    "terms for a $180,000 commitment, Northwind has mandatory vendor onboarding requirements. Our standard payment "
                    "terms are net-60, and legal requires a strict mutual NDA and master services agreement.\n\n"
                    "Alex Rivera: Thanks for outlining that, Tom. Net-60 is something our finance team can accommodate for an enterprise "
                    "contract of this size.\n\n"
                    "Tom Bradley: Payment terms are only half the battle. Our corporate infosec policy requires a complete security "
                    "evaluation. We must receive your current SOC2 Type II audit report, penetration test summaries, and completed CAIQ "
                    "security questionnaire before legal permits execution.\n\n"
                    "David Chen: Alex, to reiterate what Tom said, we also still need the custom ERP latency benchmark data you promised to "
                    "send back during our technical deep-dive. Elena needs to validate those numbers before we sign off.\n\n"
                    "Alex Rivera: Understood, Tom and David. I will make sure procurement receives our standard enterprise compliance package "
                    "and vendor guidelines so we can align our timelines.\n\n"
                    "Tom Bradley: Make sure that happens quickly, Alex. Sarah has scheduled our executive vendor review for November 20th. "
                    "If the infosec package and benchmark documentation aren't cleared by then, this deal will be pushed into next year's budget cycle.\n\n"
                    "David Chen: Let's get this finalized so we can hit our deployment targets before peak shipping season."
                ),
            },
        ],
    },
    {
        "id": "deal-2",
        "company": "Acme Freight",
        "value": 95000,
        "outcome": "won",
        "calls": [
            {
                "call_no": 1,
                "date": "2026-10-05",
                "participants": ["Alex Rivera", "Rachel Adams"],
                "transcript": (
                    "Rachel Adams: Alex, thanks for meeting. Our freight brokerage runs on AWS and GCP. Over the last six months, our "
                    "multi-cloud infrastructure costs have grown over 40%, eating into our operational margins. We currently use Datadog for "
                    "APM and their basic cloud cost module, but it's too coarse and we're paying $60,000 a year for very little actionable "
                    "optimization. We need granular Kubernetes pod-level visibility.\n\n"
                    "Alex Rivera: Rachel, that's exactly where we specialize. Unlike generic APM tools that show high-level cluster costs, "
                    "we provide pod-by-pod, namespace-level telemetry and automated recommendations for rightsizing instances and reserved capacity. "
                    "We can pinpoint underutilized resources down to specific routing microservices.\n\n"
                    "Rachel Adams: That level of granularity would be huge for our platform team. But switching or adding tools requires CFO "
                    "approval. Kevin Patel, our CFO, scrutinizes every dollar. If I bring you in front of Kevin, you need to show clear financial "
                    "justification beyond what Datadog offers.\n\n"
                    "Alex Rivera: Understood, Rachel. I promise to prepare an in-depth comparison showing how our granular optimization delivers "
                    "savings that general monitoring tools miss, tailored specifically to logistics freight workloads.\n\n"
                    "Rachel Adams: Great. I'll set up a demo call with Kevin next week."
                ),
            },
            {
                "call_no": 2,
                "date": "2026-10-15",
                "participants": ["Alex Rivera", "Kevin Patel", "Rachel Adams"],
                "transcript": (
                    "Kevin Patel: Alex, Rachel walked me through your pitch, but looking at a $95,000 annual contract gives me pause. Freight "
                    "operating margins are razor-thin right now, hovering around 3.5%. We already write a $60,000 annual check to Datadog. Convince "
                    "me why I shouldn't just ask Datadog for a discount rather than signing a new five-figure software contract.\n\n"
                    "Alex Rivera: Kevin, Datadog is great for infrastructure monitoring, but their cost module lacks automated rightsizing and "
                    "container waste attribution. In our benchmark studies, companies relying solely on APM cost dashboards leave 20% to 30% of "
                    "their cloud budget on the table. Our platform routinely identifies immediate savings that surpass the contract value in the first quarter.\n\n"
                    "Kevin Patel: That's a bold claim, Alex. My objection is that SaaS vendors always promise huge ROI, but then our internal team spends "
                    "six months on integration and the savings never materialize. What guarantee do we have that this $95,000 won't simply inflate our "
                    "software overhead?\n\n"
                    "Alex Rivera: That is a completely valid concern, Kevin. Let me put together a phased adoption proposal that ties our licensing directly "
                    "to verified savings milestones in your environment.\n\n"
                    "Kevin Patel: If you can tie your fees to proven savings, I'm willing to keep listening. Let's see what that looks like."
                ),
            },
            {
                "call_no": 3,
                "date": "2026-10-24",
                "participants": ["Alex Rivera", "Kevin Patel", "Rachel Adams"],
                "transcript": (
                    "Alex Rivera: Kevin, Rachel, thanks for reconvening. Based on Kevin's feedback, I've structured a phased-pricing pilot proposal. "
                    "Instead of committing to the full $95,000 upfront, we begin with a 60-day pilot at a nominal $10,000 onboarding fee. During those "
                    "60 days, we connect to your AWS production clusters and set a hard milestone: identifying and automating at least 20% in verified "
                    "cloud savings.\n\n"
                    "Kevin Patel: And what happens if your platform fails to reach that 20% savings threshold within the 60 days?\n\n"
                    "Alex Rivera: If we don't hit the 20% savings milestone, Acme has zero obligation to continue and the remaining $85,000 annual "
                    "contract is null and void. You keep all the optimizations discovered during the pilot.\n\n"
                    "Rachel Adams: Kevin, that completely eliminates our risk. Our engineering team can connect the read-only AWS IAM role in under an "
                    "hour, and we can immediately test our largest staging cluster.\n\n"
                    "Kevin Patel: A phased pilot with guaranteed ROI milestones is the kind of accountability I like to see, Alex. That protects our "
                    "budget and holds your product to its claims. Rachel, coordinate with Brian in procurement to initiate vendor onboarding.\n\n"
                    "Rachel Adams: I'll introduce Brian to Alex today."
                ),
            },
            {
                "call_no": 4,
                "date": "2026-11-02",
                "participants": ["Alex Rivera", "Brian Miller", "Rachel Adams"],
                "transcript": (
                    "Brian Miller: Alex, Rachel and Kevin forwarded your phased proposal. From procurement's perspective, this looks structured and "
                    "well-defined. I'm reviewing your standard Master Services Agreement and data privacy exhibit. Our standard payment terms are net-45. "
                    "Will that work for the initial $10,000 pilot invoice?\n\n"
                    "Alex Rivera: Yes, Brian, net-45 is acceptable for both the pilot fee and the subsequent annual renewal invoice.\n\n"
                    "Rachel Adams: Brian, just to share some exciting early data: we granted read-only access to our staging environment last Thursday, "
                    "and within 48 hours the platform surfaced $18,000 in annualized idle container allocations and obsolete EBS snapshots. The "
                    "recommendations took my team twenty minutes to execute.\n\n"
                    "Brian Miller: That's remarkable speed. If the tool is already showing verifiable cost reductions, that makes legal and procurement "
                    "sign-off much smoother. Our Datadog contract renewal is December 1st, so we have strong leverage to downgrade their cost add-on.\n\n"
                    "Alex Rivera: I promise to provide our finalized SOC2 Type II attestation and security whitepaper to Brian by tomorrow morning so "
                    "legal can execute without delay.\n\n"
                    "Brian Miller: Send those over, Alex. We'll have redlines finalized by Friday."
                ),
            },
            {
                "call_no": 5,
                "date": "2026-11-10",
                "participants": ["Alex Rivera", "Brian Miller", "Kevin Patel", "Rachel Adams"],
                "transcript": (
                    "Kevin Patel: Alex, I wanted to personally jump on this call to confirm that I have signed the $95,000 agreement. Brian confirmed legal "
                    "cleared all exhibits, and Rachel's early results from the pilot phase convinced me that this investment pays for itself multiple times over.\n\n"
                    "Rachel Adams: We've already reclaimed $22,000 in annualized AWS waste across our staging clusters alone. The automated rightsizing "
                    "recommendations gave our DevOps team immediate confidence.\n\n"
                    "Alex Rivera: Kevin, Rachel, Brian, thank you for your partnership. We're thrilled to welcome Acme Freight as an enterprise customer.\n\n"
                    "Kevin Patel: To be completely candid, Alex, the winning factor for me was your willingness to offer a phased-pricing pilot with guaranteed "
                    "savings milestones instead of pushing a rigid annual prepayment. That showed true confidence in your software and protected our quarterly "
                    "margins. Let's make sure implementation kicks off smoothly next week.\n\n"
                    "Alex Rivera: Our lead customer success engineer will host your kickoff session on Monday. Thank you all."
                ),
            },
        ],
    },
    {
        "id": "deal-3",
        "company": "Meridian Health Solutions",
        "value": 240000,
        "outcome": "won",
        "calls": [
            {
                "call_no": 1,
                "date": "2026-10-02",
                "participants": ["Alex Rivera", "Dr. Aris Thorne"],
                "transcript": (
                    "Dr. Aris Thorne: Alex, thank you for taking the time. Meridian operates healthcare networks across four states, and our clinical "
                    "data lake and patient portal infrastructure on Microsoft Azure have expanded dramatically. Our annual Azure cloud spend recently crossed "
                    "$1.8 million. We need an intelligent platform to allocate costs across our clinical research, hospital operations, and telemedicine divisions.\n\n"
                    "Alex Rivera: Dr. Thorne, thank you for sharing your background. We specialize in healthcare cloud cost intelligence. We map cloud "
                    "consumption to clinical service lines, departmental cost centers, and research grants with full multi-tenant visibility.\n\n"
                    "Dr. Aris Thorne: That's exactly what our executive committee has been asking for. However, in healthcare, security and compliance "
                    "are paramount. We handle protected health information under HIPAA regulations. Before we can evaluate any software, you will have to "
                    "undergo intense scrutiny from our Chief Information Security Officer, Lisa Sterling. She is extremely cautious regarding third-party "
                    "SaaS vendors.\n\n"
                    "Alex Rivera: Understood, Dr. Thorne. We take healthcare compliance seriously. We are SOC2 Type II certified, HITRUST compliant, and "
                    "routinely execute comprehensive Business Associate Agreements with healthcare clients.\n\n"
                    "Dr. Aris Thorne: Glad to hear that. I will arrange a joint review with Lisa Sterling next week."
                ),
            },
            {
                "call_no": 2,
                "date": "2026-10-12",
                "participants": ["Alex Rivera", "Dr. Aris Thorne", "Lisa Sterling"],
                "transcript": (
                    "Lisa Sterling: Alex, Dr. Thorne briefed me on your platform, but my role is safeguarding our patient data and hospital telemetry. "
                    "Healthcare organizations face relentless cyber threats, and third-party SaaS integrations are our primary vulnerability vector. "
                    "Many vendors claim compliance, but fail our mandatory 200-question security assessment.\n\n"
                    "Alex Rivera: Lisa, I appreciate your vigilance. We welcome deep technical security audits from healthcare security leaders.\n\n"
                    "Lisa Sterling: Let's get specific then. Do your telemetry ingestion collectors require access to our Azure storage accounts where "
                    "patient records reside? How do you ensure zero data persistence for clinical metadata, and what are your encryption standards in transit "
                    "and at rest?\n\n"
                    "Alex Rivera: Lisa, our architecture operates strictly on infrastructure billing metadata and resource utilization metrics. We never "
                    "inspect or store clinical records or patient identifiers. Furthermore, all telemetry uses TLS 1.3 in transit and AES-256 encryption at rest.\n\n"
                    "Lisa Sterling: Statements in a meeting are not sufficient, Alex. I need a comprehensive architecture packet, complete HITRUST certification, "
                    "and our customized Business Associate Agreement terms accepted. If you cannot provide a pre-completed CAIQ and architecture review, this "
                    "evaluation ends here.\n\n"
                    "Alex Rivera: I promise to deliver a complete security packet and schedule a technical security deep-dive with our lead architect by next Tuesday."
                ),
            },
            {
                "call_no": 3,
                "date": "2026-10-21",
                "participants": ["Alex Rivera", "Dr. Aris Thorne", "Lisa Sterling"],
                "transcript": (
                    "Alex Rivera: Lisa, Dr. Thorne, thank you for joining. Following our last discussion, I coordinated with our Chief Information Security "
                    "Officer to assemble a dedicated compliance package for Meridian. I have provided our complete SOC2 Type II report, HITRUST certification, "
                    "pre-populated CAIQ responses, and an executed BAA.\n\n"
                    "Lisa Sterling: Alex, I spent yesterday reviewing the packet with our cloud security engineers. I must commend your team: your "
                    "zero-telemetry-retention architecture and customer-managed encryption key support directly address our HIPAA compliance concerns. You also "
                    "answered all 200 questions in our vendor security assessment without generic boilerplate.\n\n"
                    "Dr. Aris Thorne: Lisa, that sounds like a major milestone. Usually vendor security reviews take our compliance team three to four months.\n\n"
                    "Lisa Sterling: It is a rare outcome, Aris. Because Alex's team proactively provided an architectural deep-dive and transparent compliance "
                    "exhibits, I am officially clearing CloudScale from a security and infosec standpoint. Alex, you have passed our security evaluation.\n\n"
                    "Alex Rivera: Thank you, Lisa. Having your endorsement as CISO gives us tremendous momentum as we engage finance.\n\n"
                    "Lisa Sterling: You earned it. I'll inform Donald Wright in finance that infosec has greenlit the platform."
                ),
            },
            {
                "call_no": 4,
                "date": "2026-10-30",
                "participants": ["Alex Rivera", "Donald Wright", "Dr. Aris Thorne"],
                "transcript": (
                    "Donald Wright: Alex, Dr. Thorne and Lisa Sterling brought your proposal to my desk. At $240,000 annually, this is an enterprise investment "
                    "for Meridian. We need to ensure that the return on investment justifies the expenditure, especially given our planned hospital expansion "
                    "into new regional facilities.\n\n"
                    "Dr. Aris Thorne: Donald, our Azure compute sprawl has resulted in over $400,000 in unallocated cluster fees this year alone. Having granular "
                    "cost attribution per clinical division will allow department heads to manage their own cloud budgets efficiently.\n\n"
                    "Donald Wright: What impressed me most was that Lisa Sterling's security team cleared this platform in less than three weeks. Normally, "
                    "healthcare compliance review stalls enterprise software for half a year. What does your rollout schedule look like?\n\n"
                    "Alex Rivera: Donald, we can deploy the platform across all four hospital regional networks within two weeks. We provide dedicated "
                    "onboarding engineers to train clinical department administrators on budgeting dashboards.\n\n"
                    "Donald Wright: If we can achieve full operational deployment before the close of Q4, I am prepared to sign off on the $240,000 contract. "
                    "Alex, please work with legal to finalize the Master Services Agreement.\n\n"
                    "Alex Rivera: I will coordinate with your legal counsel today, Donald."
                ),
            },
            {
                "call_no": 5,
                "date": "2026-11-08",
                "participants": ["Alex Rivera", "Donald Wright", "Dr. Aris Thorne", "Lisa Sterling"],
                "transcript": (
                    "Donald Wright: Alex, Dr. Thorne, Lisa, good afternoon. I am pleased to share that legal and finance have executed the $240,000 enterprise "
                    "agreement for Meridian Health Solutions. The purchase order has been generated and released to your accounts team.\n\n"
                    "Dr. Aris Thorne: This is a fantastic milestone for our clinical data operations. We can now accurately forecast infrastructure costs "
                    "for our medical research initiatives without manual spreadsheet gymnastics.\n\n"
                    "Alex Rivera: Donald, Dr. Thorne, Lisa, thank you so much for your trust and collaboration throughout this thorough evaluation.\n\n"
                    "Lisa Sterling: I want to highlight that what sealed this partnership was your proactive approach to healthcare compliance. Most SaaS "
                    "vendors treat security as an afterthought and stall our questions for months. By leading with an upfront security architecture deep-dive "
                    "and comprehensive audit documentation, you eliminated our biggest operational risk.\n\n"
                    "Donald Wright: Lisa is spot on. Trust and security speed made this a unanimous executive decision. We look forward to kicking off "
                    "implementation next week.\n\n"
                    "Alex Rivera: Thank you all. Our enterprise healthcare onboarding team is prepared for Monday's kickoff."
                ),
            },
        ],
    },
    {
        "id": "deal-4",
        "company": "Apex Retail Technologies",
        "value": 120000,
        "outcome": "lost",
        "calls": [
            {
                "call_no": 1,
                "date": "2026-10-08",
                "participants": ["Alex Rivera", "Jason Burke"],
                "transcript": (
                    "Jason Burke: Alex, thanks for connecting. Apex operates e-commerce and retail inventory systems for major regional chains. As we head "
                    "into Q4 holiday shopping preparation, our AWS infrastructure scales up significantly. We're currently spending around $110,000 a month "
                    "on cloud infrastructure, and our executive team is demanding better cost controls.\n\n"
                    "Alex Rivera: Jason, retail e-commerce during peak season is a high-stakes environment. Our platform offers real-time Kubernetes autoscaling "
                    "recommendations and dynamic Spot instance optimization to cut compute costs during high-traffic surges without risking site reliability.\n\n"
                    "Jason Burke: That dynamic optimization sounds compelling, Alex. Right now, my engineers spend hours manually checking AWS Cost Explorer, "
                    "but its reports are 24 hours behind and don't correlate with customer cart transactions. I'd love to bring this to our VP of Finance, "
                    "Amanda Cole, but she is very strict on budget.\n\n"
                    "Alex Rivera: I understand, Jason. Our typical retail customer saves over $200,000 annually. I'll prepare a tailored demonstration for "
                    "Amanda showing how we handle e-commerce traffic spikes.\n\n"
                    "Jason Burke: Sounds good, Alex. I'll get Amanda on the calendar for next week."
                ),
            },
            {
                "call_no": 2,
                "date": "2026-10-18",
                "participants": ["Alex Rivera", "Amanda Cole", "Jason Burke"],
                "transcript": (
                    "Amanda Cole: Alex, Jason has shared his enthusiasm for your platform, but as VP of Finance, I have to look at the numbers. You quoted an "
                    "annual contract of $120,000 payable upfront. We are heading into retail holiday season where margins are pressurized and supply chain costs "
                    "are up. I cannot justify $120,000 for a third-party cost tool when AWS Cost Explorer is free.\n\n"
                    "Alex Rivera: Amanda, while AWS Cost Explorer is free, it provides backward-looking data and lacks automated rightsizing. Our enterprise "
                    "clients typically see a 3x return on their investment within the first six months.\n\n"
                    "Amanda Cole: ROI promises don't solve my immediate cash flow challenge, Alex. Our board has placed tight restrictions on fourth-quarter "
                    "capital expenditures. Can you offer flexible terms, such as a monthly pilot or a performance-based pricing model that lowers our upfront risk?\n\n"
                    "Alex Rivera: Unfortunately, Amanda, our company policy requires annual upfront commitments for enterprise tiers. The best concession I "
                    "can offer is a 5% discount on the annual contract, bringing it to $114,000.\n\n"
                    "Amanda Cole: A 5% discount does not address the upfront cash outlay, Alex. That leaves all the risk on our balance sheet.\n\n"
                    "Jason Burke: Amanda, if we can reduce compute waste by even 15%, the tool pays for itself.\n\n"
                    "Amanda Cole: That is speculative, Jason. Alex, we need more flexibility than a rigid annual contract."
                ),
            },
            {
                "call_no": 3,
                "date": "2026-10-28",
                "participants": ["Alex Rivera", "Greg Sanders", "Jason Burke"],
                "transcript": (
                    "Greg Sanders: Alex, Jason asked me to join to see if we can find common ground on commercial terms. Amanda Cole from finance is holding a "
                    "firm line: Apex cannot execute an annual upfront commitment of $114,000 in Q4. If your company could structure a 90-day phased pilot or "
                    "quarterly billing milestones tied to demonstrated savings, we could obtain executive sign-off.\n\n"
                    "Alex Rivera: Greg, I hear where Amanda and you are coming from. However, our management insists on annual upfront terms to maintain our "
                    "enterprise valuation metrics. I can offer extended payment terms of net-45, but the contract must remain an annual commitment.\n\n"
                    "Greg Sanders: Net-45 does not change the fiscal year expenditure, Alex. It still commits Apex to the full sum before we have verified "
                    "whether your algorithms work on our dynamic retail workloads.\n\n"
                    "Jason Burke: Alex, is there really no room for a milestone-based pilot? We saw another competitor offer a sixty-day pilot where fees "
                    "scaled only after verified savings.\n\n"
                    "Alex Rivera: Our platform's capabilities are superior to competitors, Jason, and we believe the value justifies our standard contract structure.\n\n"
                    "Greg Sanders: I understand your position, Alex, but without contract flexibility, this will not pass our finance review committee."
                ),
            },
            {
                "call_no": 4,
                "date": "2026-11-06",
                "participants": ["Alex Rivera", "Amanda Cole", "Jason Burke"],
                "transcript": (
                    "Amanda Cole: Alex, Jason, thank you for joining this call. Our executive budget committee met yesterday afternoon to finalize all "
                    "remaining Q4 expenditures. Because your team was unable to provide a phased pilot or milestone-based risk sharing, our committee has "
                    "decided to implement a full freeze on new third-party SaaS tools for the remainder of this fiscal year.\n\n"
                    "Jason Burke: Amanda, it's unfortunate we couldn't make this work. My team will have to build internal monitoring scripts to scrape AWS "
                    "CloudWatch metrics manually.\n\n"
                    "Amanda Cole: I recognize that puts additional burden on engineering, Jason, but committing over $114,000 upfront without guaranteed "
                    "milestone protections is a financial risk we cannot take in this retail climate. Alex, we appreciate your time, but Apex will not be "
                    "moving forward with this contract.\n\n"
                    "Alex Rivera: Thank you for the candid update, Amanda and Jason. If your budget situation shifts in the new fiscal year, please feel "
                    "free to reach back out.\n\n"
                    "Amanda Cole: We will evaluate internal progress in Q2. Goodbye, Alex."
                ),
            },
        ],
    },
    {
        "id": "deal-5",
        "company": "Cascade Media Group",
        "value": 65000,
        "outcome": "lost",
        "calls": [
            {
                "call_no": 1,
                "date": "2026-10-04",
                "participants": ["Alex Rivera", "Maya Lin"],
                "transcript": (
                    "Maya Lin: Alex, thanks for hopping on. Cascade Media runs digital video streaming and podcast syndication across Google Cloud Platform. "
                    "Over the last year, our transcode rendering workloads and multi-region CDN egress costs have skyrocketed to nearly $80,000 per month. "
                    "Our engineering team is looking for a FinOps platform that can give us automated insight into GCP BigQuery queries and Kubernetes cluster "
                    "resource waste.\n\n"
                    "Alex Rivera: Maya, great to meet you. Cascade's streaming profile fits our platform perfectly. We integrate directly with GCP Cloud "
                    "Billing and Google Kubernetes Engine to track pod-level resource utilization and flag unoptimized media transcode jobs.\n\n"
                    "Maya Lin: That's exactly what we need, Alex. However, before we can connect anything to our production GCP projects, our compliance "
                    "department requires a thorough security review. We handle licensed digital assets and partner media streams, so our VP of Information "
                    "Security, Robert Vance, is extremely strict about third-party vendor integrations.\n\n"
                    "Alex Rivera: Understood, Maya. We are SOC2 Type II certified and maintain robust enterprise security controls. I would be happy to walk "
                    "Robert through our security architecture.\n\n"
                    "Maya Lin: I'll schedule a security review call with Robert for next week."
                ),
            },
            {
                "call_no": 2,
                "date": "2026-10-14",
                "participants": ["Alex Rivera", "Maya Lin", "Robert Vance"],
                "transcript": (
                    "Robert Vance: Alex, Maya introduced your platform, but my responsibility as VP of InfoSec is ensuring our media infrastructure remains "
                    "locked down. Granting a third-party SaaS tool read and analytics access to our Google Cloud environment carries significant compliance "
                    "implications. We cannot allow external agents to access telemetry without verifying data residency, penetration testing, and SOC2 "
                    "Type II compliance.\n\n"
                    "Alex Rivera: Robert, I completely understand your security posture. Our platform functions strictly with least-privilege IAM permissions "
                    "and requires only metadata access. We never touch media payload files or user credentials.\n\n"
                    "Robert Vance: That sounds good in theory, Alex, but our corporate policy requires formal documentation. I need to review your latest "
                    "SOC2 Type II audit report, independent penetration test summary, and data protection addendum before we can authorize even a sandbox "
                    "integration. Can you send those over?\n\n"
                    "Alex Rivera: Absolutely, Robert. I promise I will email our complete SOC2 Type II audit report, third-party pen-test summary, and standard "
                    "security whitepaper to you by this Friday.\n\n"
                    "Robert Vance: Send those by Friday, Alex. If everything checks out, I will sign off on the security clearance for Maya's team.\n\n"
                    "Maya Lin: Looking forward to reviewing the docs, Alex."
                ),
            },
            {
                "call_no": 3,
                "date": "2026-10-26",
                "participants": ["Alex Rivera", "Chloe Bennett", "Maya Lin"],
                "transcript": (
                    "Maya Lin: Alex, Chloe from legal joined us today, but unfortunately Robert Vance couldn't make it. To be candid, Alex, we are in a "
                    "difficult spot. It has been almost two weeks since our call with Robert, and he told me this morning that he never received the SOC2 "
                    "audit report or penetration test results you promised to send by that Friday.\n\n"
                    "Chloe Bennett: Alex, without those security exhibits, our legal department cannot advance the Master Services Agreement. Cascade's "
                    "vendor governance requires infosec sign-off as a prerequisite for contract review. Right now, this procurement process is completely stalled.\n\n"
                    "Alex Rivera: Maya, Chloe, I sincerely apologize. Our compliance team was updating our annual documentation audit, which caused an "
                    "unexpected delay on my end. I promise to deliver those documents to Robert and Chloe by tomorrow afternoon.\n\n"
                    "Maya Lin: Alex, this delay is putting our timeline at severe risk. Our fiscal quarter closes in two weeks, and our current monitoring "
                    "vendor has already approached us with an early renewal discount. Robert's team is growing skeptical.\n\n"
                    "Chloe Bennett: Please send the files immediately, Alex. Every day of delay decreases the likelihood of closing this deal before the deadline."
                ),
            },
            {
                "call_no": 4,
                "date": "2026-11-05",
                "participants": ["Alex Rivera", "Maya Lin", "Robert Vance"],
                "transcript": (
                    "Robert Vance: Alex, thank you for joining. I asked Maya to arrange this call because I wanted to deliver our decision directly. We "
                    "received your security documents late last week, nearly three weeks after our initial request. Upon review, our infosec committee noted "
                    "that you still did not provide the dedicated security architecture session we requested.\n\n"
                    "Maya Lin: Alex, our leadership team was operating under strict quarterly deadlines to finalize our cloud monitoring strategy.\n\n"
                    "Robert Vance: Given the repeated delays in receiving compliance documentation and the absence of a proactive security review, our "
                    "risk governance committee voted to deny third-party approval for CloudScale. We cannot risk onboarding a vendor that does not treat "
                    "compliance commitments with urgency. As a result, we have executed an annual renewal with our incumbent security-cleared monitoring partner.\n\n"
                    "Alex Rivera: Robert, Maya, I deeply regret that our documentation delay impacted your timeline and decision. I understand your governance obligations.\n\n"
                    "Robert Vance: Security and reliability are non-negotiable for Cascade Media. We will not be pursuing this agreement. Thank you for your time, Alex.\n\n"
                    "Maya Lin: Thank you for the effort, Alex. Take care."
                ),
            },
        ],
    },
    {
        "id": "deal-6",
        "company": "Zenith Aerospace Systems",
        "value": 310000,
        "outcome": None,
        "calls": [
            {
                "call_no": 1,
                "date": "2026-10-10",
                "participants": ["Alex Rivera", "Vikram Malhotra"],
                "transcript": (
                    "Vikram Malhotra: Alex, thanks for meeting today. Zenith develops avionics telemetry and satellite communications infrastructure. "
                    "Our engineering operations span both commercial AWS regions and dedicated AWS GovCloud environments, alongside legacy on-premise compute "
                    "clusters. Our annual cloud bill exceeds $3.5 million, and we have zero unified visibility across our hybrid environments.\n\n"
                    "Alex Rivera: Vikram, it's an honor to speak with Zenith. Our platform was architected specifically to handle hybrid enterprise "
                    "environments. We can ingest utilization telemetry from AWS GovCloud as well as private Kubernetes clusters, giving your engineering "
                    "leadership a single unified dashboard for FinOps governance.\n\n"
                    "Vikram Malhotra: That hybrid GovCloud capability is critical for us, Alex. But because we operate in aerospace and defense, compliance "
                    "is our strictest filter. We are subject to ITAR regulations and strict federal data handling mandates. If your tool cannot meet GovCloud "
                    "isolation standards, our IT compliance director will veto it immediately.\n\n"
                    "Alex Rivera: We completely understand the aerospace compliance landscape, Vikram. Our platform supports isolated tenant deployments "
                    "with zero telemetry egress outside authorized boundaries. I promise to share our federal compliance overview and GovCloud architectural "
                    "blueprint before our next session.\n\n"
                    "Vikram Malhotra: Excellent, Alex. I will invite our compliance director, Samuel Ward, to our next discussion."
                ),
            },
            {
                "call_no": 2,
                "date": "2026-10-20",
                "participants": ["Alex Rivera", "Samuel Ward", "Vikram Malhotra"],
                "transcript": (
                    "Samuel Ward: Alex, Vikram shared your GovCloud architectural blueprint. While the technical design is well thought out, my role is "
                    "enforcing strict compliance with federal regulatory frameworks. Zenith cannot deploy third-party software that touches mission-critical "
                    "infrastructure without verified FedRAMP Moderate controls and strict ITAR boundary assurances.\n\n"
                    "Alex Rivera: Samuel, we take aerospace compliance very seriously. Our dedicated GovCloud deployment runs completely isolated within "
                    "AWS GovCloud US regions, utilizing FIPS 140-2 validated cryptographic modules. No telemetry metadata ever crosses into commercial cloud infrastructure.\n\n"
                    "Samuel Ward: That addresses the perimeter boundary, Alex, but what about continuous audit logging and role-based access control? Our "
                    "security audit team requires multi-factor authentication with hardware tokens and complete tamper-evident audit trails.\n\n"
                    "Alex Rivera: Our platform supports SAML 2.0 with mandatory hardware MFA and immutable audit logging piped directly to your internal "
                    "security information and event management system. I promise to provide our FedRAMP Moderate control implementation summary and ITAR "
                    "compliance brief by next Wednesday.\n\n"
                    "Samuel Ward: If that documentation validates your claims, I will allow the technical evaluation to proceed to our Chief Financial "
                    "Officer, Evelyn Cross, for budget review.\n\n"
                    "Vikram Malhotra: Thanks, Samuel. Let's keep this momentum going."
                ),
            },
            {
                "call_no": 3,
                "date": "2026-10-31",
                "participants": ["Alex Rivera", "Evelyn Cross", "Samuel Ward"],
                "transcript": (
                    "Evelyn Cross: Alex, Samuel confirmed that your compliance documentation passed preliminary audit scrutiny, which brings us to the "
                    "financial commitment. Your proposed $310,000 annual licensing fee is a major capital investment. In aerospace contracting, our project "
                    "budgets are tied to strict multi-year program deliverables. What kind of return and multi-year pricing structure can you offer Zenith?\n\n"
                    "Alex Rivera: Evelyn, thank you for joining. For an enterprise of Zenith's scale, our customers typically achieve an 18% to 25% "
                    "reduction in compute waste within the first 90 days, which represents over $600,000 in annual recurring savings. For multi-year "
                    "agreements, we can structure a tiered discounting model that scales with your fleet deployment.\n\n"
                    "Evelyn Cross: A tiered multi-year model is certainly appealing, Alex. However, before I present this to our executive board, I need a "
                    "detailed three-year total cost of ownership analysis and a clear payback schedule. We cannot commit $310,000 without verified milestone "
                    "protections.\n\n"
                    "Samuel Ward: From my side, Alex, our security team is currently conducting a formal penetration test on your GovCloud sandbox. We expect "
                    "results within two weeks.\n\n"
                    "Alex Rivera: I will build out the three-year financial model and coordinate closely with Samuel's audit team."
                ),
            },
            {
                "call_no": 4,
                "date": "2026-11-14",
                "participants": ["Alex Rivera", "Evelyn Cross", "Samuel Ward", "Vikram Malhotra"],
                "transcript": (
                    "Evelyn Cross: Alex, thank you for sending over the three-year total cost of ownership model. The multi-year discounting structure "
                    "aligns much better with our federal contract cycles. However, our legal team is still reviewing your indemnification clauses and "
                    "government data rights addendum.\n\n"
                    "Samuel Ward: On the security front, Alex, our penetration testing team completed their assessment of the GovCloud sandbox yesterday. "
                    "They identified zero critical vulnerabilities, but did submit three minor inquiries regarding session timeout configurations. I expect "
                    "our infosec committee to issue final clearance next week.\n\n"
                    "Vikram Malhotra: The engineering team has already mapped out our initial deployment phase across two satellite telemetry ground stations "
                    "as soon as legal gives the green light.\n\n"
                    "Alex Rivera: That is fantastic progress across all fronts, Evelyn, Samuel, and Vikram. I have already submitted the revised "
                    "indemnification wording to your legal team for expedited review.\n\n"
                    "Evelyn Cross: We will convene our executive procurement committee next Tuesday once Samuel's final infosec memo is filed. If legal "
                    "approves the updated addendum, we anticipate finalizing the contract before month-end.\n\n"
                    "Alex Rivera: I will remain on standby to assist legal and procurement with any final questions."
                ),
            },
        ],
    },
]

DEMO_CALL_5 = {
    "call_no": 5,
    "date": "2026-11-20",
    "participants": ["Alex Rivera", "David Chen", "Sarah Jenkins", "Tom Bradley"],
    "transcript": (
        "Sarah Jenkins: Alex, let's get straight to the point. We reviewed our capital allocation for the upcoming quarter, "
        "and committing $180,000 upfront remains an insurmountable hurdle under our current spending freeze. Unless we can "
        "structure a low-risk phased pilot with guaranteed ROI milestones, this evaluation stops today.\n\n"
        "Tom Bradley: And to compound that, Alex, our infosec review is completely blocked. When I met with compliance yesterday, "
        "they confirmed we still have not received the SOC2 Type II audit report and security audit results that you promised "
        "David weeks ago. Without that documentation, corporate compliance will not permit vendor approval.\n\n"
        "David Chen: Alex, I really want this platform for our engineering team, but my hands are tied. Elena and I love the tooling, "
        "but without the security audit results in hand and a way to satisfy Sarah's quarterly budget restrictions, we cannot proceed.\n\n"
        "Alex Rivera: Sarah, Tom, David, I hear you loud and clear, and I apologize for the delay on that compliance documentation. "
        "I have our updated SOC2 Type II report and third-party penetration summary ready to transmit to Tom's inbox immediately following this call.\n\n"
        "Sarah Jenkins: That resolves the compliance blocker, but what about the financial exposure of the upfront $180,000 fee?\n\n"
        "Alex Rivera: We can deploy a 60-day phased-pricing pilot: an initial $20,000 implementation phase, where the remaining $160,000 "
        "balance only activates once we demonstrate at least $50,000 in verified cloud waste reduction across your first four distribution hubs.\n\n"
        "Sarah Jenkins: A milestone-based pilot tied to verified savings directly protects our quarterly cash flow. Send that revised contract over today."
    ),
}

def main():
    os.makedirs("data", exist_ok=True)
    with open("data/deals.json", "w", encoding="utf-8") as f:
        json.dump(DEALS, f, indent=2)
    print("Wrote data/deals.json")

    with open("data/demo_call_5.json", "w", encoding="utf-8") as f:
        json.dump(DEMO_CALL_5, f, indent=2)
    print("Wrote data/demo_call_5.json")

if __name__ == "__main__":
    main()
