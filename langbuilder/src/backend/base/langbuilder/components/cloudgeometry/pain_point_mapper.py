"""
Pain Point Mapper - LangBuilder Custom Component

Maps (role, industry, service_type) combinations to specific business pain points
for generating personalized content.

Author: CloudGeometry
Project: Carter's Agents - Content Engine
"""

from langbuilder.custom import Component
from langbuilder.inputs.inputs import HandleInput
from langbuilder.io import Output
from langbuilder.schema import Data


class PainPointMapper(Component):
    """
    Maps role + industry + service to specific business pain points.

    This component is used by the Content Engine agent to determine
    which pain points to emphasize in AI-generated executive summaries,
    ensuring content resonates with the prospect's specific concerns
    based on their role, industry, AND the CloudGeometry service.
    """

    display_name = "Pain Point Mapper"
    description = "Maps role + industry + service to specific business pain points for personalized content"
    icon = "target"
    name = "PainPointMapper"

    # CloudGeometry core services
    SERVICES = [
        "AI Transformation",
        "App Modernization",
        "Cloud Migration",
        "DevOps Acceleration",
        "Data Platform",
        "Managed Services",
    ]

    # Pain point matrix - tuple (role, industry, service_type) -> pain point string
    PAIN_POINT_MATRIX = {
        # ═══════════════════════════════════════════════════════════════
        # AI TRANSFORMATION
        # ═══════════════════════════════════════════════════════════════

        # CFO + AI Transformation
        ("CFO", "Healthcare", "AI Transformation"): "AI implementation ROI and HIPAA-compliant ML infrastructure costs",
        ("CFO", "Fintech", "AI Transformation"): "AI/ML infrastructure costs and fraud detection ROI",
        ("CFO", "Technology", "AI Transformation"): "AI R&D costs and time-to-market for ML features",
        ("CFO", "Retail", "AI Transformation"): "personalization AI costs and recommendation engine ROI",
        ("CFO", "Manufacturing", "AI Transformation"): "predictive maintenance AI costs and production optimization ROI",

        # CTO + AI Transformation
        ("CTO", "Healthcare", "AI Transformation"): "deploying clinical AI models with HIPAA compliance and data governance",
        ("CTO", "Fintech", "AI Transformation"): "real-time ML inference for fraud detection and model versioning",
        ("CTO", "Technology", "AI Transformation"): "ML platform architecture, model serving, and GPU infrastructure",
        ("CTO", "Retail", "AI Transformation"): "recommendation engine architecture and real-time personalization",
        ("CTO", "Manufacturing", "AI Transformation"): "edge AI deployment for predictive maintenance and quality control",

        # CIO + AI Transformation
        ("CIO", "Healthcare", "AI Transformation"): "AI governance, clinical decision support integration, and vendor selection",
        ("CIO", "Fintech", "AI Transformation"): "AI risk management, explainability requirements, and regulatory compliance",
        ("CIO", "Technology", "AI Transformation"): "AI strategy, build vs buy decisions, and talent acquisition",
        ("CIO", "Retail", "AI Transformation"): "AI-driven customer experience strategy and data unification",
        ("CIO", "Manufacturing", "AI Transformation"): "Industry 4.0 AI roadmap and OT/IT integration strategy",

        # VP Engineering + AI Transformation
        ("VP Engineering", "Healthcare", "AI Transformation"): "ML pipeline development velocity with compliance gates",
        ("VP Engineering", "Fintech", "AI Transformation"): "rapid ML model iteration with audit trails and testing",
        ("VP Engineering", "Technology", "AI Transformation"): "ML engineering productivity and experiment tracking",
        ("VP Engineering", "Retail", "AI Transformation"): "A/B testing infrastructure for ML models at scale",
        ("VP Engineering", "Manufacturing", "AI Transformation"): "deploying ML models to edge devices reliably",

        # Engineering Manager + AI Transformation
        ("Engineering Manager", "Healthcare", "AI Transformation"): "upskilling team on ML while maintaining compliance",
        ("Engineering Manager", "Fintech", "AI Transformation"): "balancing ML innovation with security requirements",
        ("Engineering Manager", "Technology", "AI Transformation"): "ML tooling standardization and team productivity",
        ("Engineering Manager", "Retail", "AI Transformation"): "cross-functional ML projects and data science collaboration",
        ("Engineering Manager", "Manufacturing", "AI Transformation"): "ML model maintenance and production reliability",

        # ═══════════════════════════════════════════════════════════════
        # APP MODERNIZATION
        # ═══════════════════════════════════════════════════════════════

        # CFO + App Modernization
        ("CFO", "Healthcare", "App Modernization"): "legacy EHR modernization costs and compliance risk during migration",
        ("CFO", "Fintech", "App Modernization"): "core banking modernization costs and regulatory continuity",
        ("CFO", "Technology", "App Modernization"): "technical debt reduction ROI and modernization budget planning",
        ("CFO", "Retail", "App Modernization"): "e-commerce platform modernization costs and revenue continuity",
        ("CFO", "Manufacturing", "App Modernization"): "MES/ERP modernization costs and production continuity",

        # CTO + App Modernization
        ("CTO", "Healthcare", "App Modernization"): "modernizing legacy healthcare systems while maintaining HIPAA compliance",
        ("CTO", "Fintech", "App Modernization"): "core banking modernization, API-first architecture, and data migration",
        ("CTO", "Technology", "App Modernization"): "monolith decomposition, containerization, and microservices adoption",
        ("CTO", "Retail", "App Modernization"): "headless commerce architecture and omnichannel platform modernization",
        ("CTO", "Manufacturing", "App Modernization"): "legacy SCADA/MES modernization and cloud-edge hybrid architecture",

        # CIO + App Modernization
        ("CIO", "Healthcare", "App Modernization"): "EHR modernization strategy, vendor lock-in, and interoperability",
        ("CIO", "Fintech", "App Modernization"): "core banking transformation roadmap and regulatory alignment",
        ("CIO", "Technology", "App Modernization"): "technical debt governance and modernization prioritization",
        ("CIO", "Retail", "App Modernization"): "omnichannel platform strategy and vendor consolidation",
        ("CIO", "Manufacturing", "App Modernization"): "OT modernization roadmap and IT/OT convergence",

        # VP Engineering + App Modernization
        ("VP Engineering", "Healthcare", "App Modernization"): "incremental modernization with zero downtime and compliance",
        ("VP Engineering", "Fintech", "App Modernization"): "strangler fig pattern execution with transaction integrity",
        ("VP Engineering", "Technology", "App Modernization"): "microservices decomposition and team autonomy",
        ("VP Engineering", "Retail", "App Modernization"): "modernizing during peak seasons without disruption",
        ("VP Engineering", "Manufacturing", "App Modernization"): "production system modernization with safety guarantees",

        # Engineering Manager + App Modernization
        ("Engineering Manager", "Healthcare", "App Modernization"): "team productivity during legacy modernization",
        ("Engineering Manager", "Fintech", "App Modernization"): "managing dual-stack expertise during transition",
        ("Engineering Manager", "Technology", "App Modernization"): "balancing feature work with modernization efforts",
        ("Engineering Manager", "Retail", "App Modernization"): "coordinating modernization across distributed teams",
        ("Engineering Manager", "Manufacturing", "App Modernization"): "legacy system knowledge transfer and documentation",

        # ═══════════════════════════════════════════════════════════════
        # CLOUD MIGRATION
        # ═══════════════════════════════════════════════════════════════

        # CFO + Cloud Migration
        ("CFO", "Healthcare", "Cloud Migration"): "cloud migration costs, HIPAA compliance in cloud, and TCO optimization",
        ("CFO", "Fintech", "Cloud Migration"): "cloud migration ROI, regulatory compliance costs, and vendor pricing",
        ("CFO", "Technology", "Cloud Migration"): "cloud cost optimization, reserved capacity planning, and FinOps",
        ("CFO", "Retail", "Cloud Migration"): "cloud costs during peak seasons and capacity planning",
        ("CFO", "Manufacturing", "Cloud Migration"): "hybrid cloud costs and edge infrastructure investment",

        # CTO + Cloud Migration
        ("CTO", "Healthcare", "Cloud Migration"): "HIPAA-compliant cloud architecture and data residency requirements",
        ("CTO", "Fintech", "Cloud Migration"): "secure cloud architecture, PCI-DSS compliance, and multi-region setup",
        ("CTO", "Technology", "Cloud Migration"): "cloud-native architecture, multi-cloud strategy, and DR design",
        ("CTO", "Retail", "Cloud Migration"): "auto-scaling architecture and global CDN deployment",
        ("CTO", "Manufacturing", "Cloud Migration"): "hybrid cloud architecture and edge-to-cloud connectivity",

        # CIO + Cloud Migration
        ("CIO", "Healthcare", "Cloud Migration"): "cloud vendor selection, data governance, and compliance strategy",
        ("CIO", "Fintech", "Cloud Migration"): "cloud risk management, exit strategy, and regulatory alignment",
        ("CIO", "Technology", "Cloud Migration"): "multi-cloud governance, cost management, and security posture",
        ("CIO", "Retail", "Cloud Migration"): "cloud strategy alignment with business growth and M&A",
        ("CIO", "Manufacturing", "Cloud Migration"): "cloud adoption roadmap and IT/OT convergence in cloud",

        # VP Engineering + Cloud Migration
        ("VP Engineering", "Healthcare", "Cloud Migration"): "zero-downtime migration with compliance validation",
        ("VP Engineering", "Fintech", "Cloud Migration"): "database migration with transaction integrity",
        ("VP Engineering", "Technology", "Cloud Migration"): "lift-and-shift vs refactor decisions and team execution",
        ("VP Engineering", "Retail", "Cloud Migration"): "migration during business-as-usual with minimal risk",
        ("VP Engineering", "Manufacturing", "Cloud Migration"): "OT system migration with production continuity",

        # Engineering Manager + Cloud Migration
        ("Engineering Manager", "Healthcare", "Cloud Migration"): "team upskilling on cloud while maintaining operations",
        ("Engineering Manager", "Fintech", "Cloud Migration"): "cloud certifications and security training",
        ("Engineering Manager", "Technology", "Cloud Migration"): "cloud skills development and on-call transition",
        ("Engineering Manager", "Retail", "Cloud Migration"): "managing migration sprints during feature development",
        ("Engineering Manager", "Manufacturing", "Cloud Migration"): "coordinating cloud migration with production schedules",

        # ═══════════════════════════════════════════════════════════════
        # DEVOPS ACCELERATION
        # ═══════════════════════════════════════════════════════════════

        # CFO + DevOps Acceleration
        ("CFO", "Healthcare", "DevOps Acceleration"): "DevOps tooling costs and compliance automation ROI",
        ("CFO", "Fintech", "DevOps Acceleration"): "DevOps investment ROI and audit automation savings",
        ("CFO", "Technology", "DevOps Acceleration"): "platform engineering costs and developer productivity ROI",
        ("CFO", "Retail", "DevOps Acceleration"): "faster time-to-market ROI and deployment automation savings",
        ("CFO", "Manufacturing", "DevOps Acceleration"): "DevOps for OT systems and automation infrastructure costs",

        # CTO + DevOps Acceleration
        ("CTO", "Healthcare", "DevOps Acceleration"): "CI/CD pipelines with compliance gates and audit trails",
        ("CTO", "Fintech", "DevOps Acceleration"): "secure CI/CD, automated compliance checks, and deployment safety",
        ("CTO", "Technology", "DevOps Acceleration"): "platform engineering, internal developer platforms, and GitOps",
        ("CTO", "Retail", "DevOps Acceleration"): "rapid deployment pipelines and feature flag infrastructure",
        ("CTO", "Manufacturing", "DevOps Acceleration"): "OT deployment automation and production-safe releases",

        # CIO + DevOps Acceleration
        ("CIO", "Healthcare", "DevOps Acceleration"): "DevOps governance, tool standardization, and compliance alignment",
        ("CIO", "Fintech", "DevOps Acceleration"): "DevOps risk management and regulatory audit readiness",
        ("CIO", "Technology", "DevOps Acceleration"): "DevOps maturity roadmap and organizational transformation",
        ("CIO", "Retail", "DevOps Acceleration"): "DevOps metrics and business alignment",
        ("CIO", "Manufacturing", "DevOps Acceleration"): "IT/OT DevOps convergence and safety standards",

        # VP Engineering + DevOps Acceleration
        ("VP Engineering", "Healthcare", "DevOps Acceleration"): "deployment frequency with compliance and quality gates",
        ("VP Engineering", "Fintech", "DevOps Acceleration"): "rapid releases with audit trails and rollback capabilities",
        ("VP Engineering", "Technology", "DevOps Acceleration"): "developer experience, platform engineering, and self-service",
        ("VP Engineering", "Retail", "DevOps Acceleration"): "high-velocity deployments during campaigns and sales",
        ("VP Engineering", "Manufacturing", "DevOps Acceleration"): "safe deployments to production systems",

        # Engineering Manager + DevOps Acceleration
        ("Engineering Manager", "Healthcare", "DevOps Acceleration"): "on-call burden and incident response optimization",
        ("Engineering Manager", "Fintech", "DevOps Acceleration"): "deployment confidence and change management",
        ("Engineering Manager", "Technology", "DevOps Acceleration"): "team productivity and tooling standardization",
        ("Engineering Manager", "Retail", "DevOps Acceleration"): "deployment coordination across distributed teams",
        ("Engineering Manager", "Manufacturing", "DevOps Acceleration"): "production deployment scheduling and safety",

        # ═══════════════════════════════════════════════════════════════
        # DATA PLATFORM
        # ═══════════════════════════════════════════════════════════════

        # CFO + Data Platform
        ("CFO", "Healthcare", "Data Platform"): "data infrastructure costs and analytics ROI with HIPAA compliance",
        ("CFO", "Fintech", "Data Platform"): "data platform costs and real-time analytics ROI",
        ("CFO", "Technology", "Data Platform"): "data infrastructure spend and self-service analytics ROI",
        ("CFO", "Retail", "Data Platform"): "customer data platform costs and personalization ROI",
        ("CFO", "Manufacturing", "Data Platform"): "IoT data platform costs and predictive analytics ROI",

        # CTO + Data Platform
        ("CTO", "Healthcare", "Data Platform"): "HIPAA-compliant data lake, PHI governance, and analytics infrastructure",
        ("CTO", "Fintech", "Data Platform"): "real-time data pipelines, event streaming, and data mesh architecture",
        ("CTO", "Technology", "Data Platform"): "data lake architecture, lakehouse patterns, and data mesh adoption",
        ("CTO", "Retail", "Data Platform"): "customer 360 platform, real-time personalization, and CDP architecture",
        ("CTO", "Manufacturing", "Data Platform"): "IoT data ingestion, time-series databases, and edge analytics",

        # CIO + Data Platform
        ("CIO", "Healthcare", "Data Platform"): "data governance, PHI access controls, and interoperability standards",
        ("CIO", "Fintech", "Data Platform"): "data governance, lineage, and regulatory reporting infrastructure",
        ("CIO", "Technology", "Data Platform"): "data strategy, governance framework, and self-service enablement",
        ("CIO", "Retail", "Data Platform"): "customer data strategy, privacy compliance, and vendor consolidation",
        ("CIO", "Manufacturing", "Data Platform"): "OT data governance and Industry 4.0 data strategy",

        # VP Engineering + Data Platform
        ("VP Engineering", "Healthcare", "Data Platform"): "data pipeline reliability and PHI data access patterns",
        ("VP Engineering", "Fintech", "Data Platform"): "streaming data pipelines and exactly-once processing",
        ("VP Engineering", "Technology", "Data Platform"): "data engineering productivity and pipeline orchestration",
        ("VP Engineering", "Retail", "Data Platform"): "real-time data ingestion and customer event processing",
        ("VP Engineering", "Manufacturing", "Data Platform"): "IoT data pipeline reliability and edge processing",

        # Engineering Manager + Data Platform
        ("Engineering Manager", "Healthcare", "Data Platform"): "data engineering team skills and PHI handling training",
        ("Engineering Manager", "Fintech", "Data Platform"): "data quality ownership and pipeline monitoring",
        ("Engineering Manager", "Technology", "Data Platform"): "data engineering best practices and tooling",
        ("Engineering Manager", "Retail", "Data Platform"): "cross-functional data projects and analytics support",
        ("Engineering Manager", "Manufacturing", "Data Platform"): "IoT data skills and edge computing expertise",

        # ═══════════════════════════════════════════════════════════════
        # MANAGED SERVICES
        # ═══════════════════════════════════════════════════════════════

        # CFO + Managed Services
        ("CFO", "Healthcare", "Managed Services"): "operational costs, SLA guarantees, and compliance management fees",
        ("CFO", "Fintech", "Managed Services"): "managed services costs vs in-house and compliance coverage",
        ("CFO", "Technology", "Managed Services"): "OpEx predictability and infrastructure management costs",
        ("CFO", "Retail", "Managed Services"): "seasonal scaling costs and pay-per-use managed services",
        ("CFO", "Manufacturing", "Managed Services"): "24/7 operations costs and OT managed services pricing",

        # CTO + Managed Services
        ("CTO", "Healthcare", "Managed Services"): "SLA guarantees, HIPAA compliance responsibility, and incident response",
        ("CTO", "Fintech", "Managed Services"): "security operations, compliance monitoring, and DR guarantees",
        ("CTO", "Technology", "Managed Services"): "infrastructure reliability, SRE practices, and vendor management",
        ("CTO", "Retail", "Managed Services"): "peak traffic handling, auto-scaling, and performance SLAs",
        ("CTO", "Manufacturing", "Managed Services"): "OT system uptime, edge management, and hybrid operations",

        # CIO + Managed Services
        ("CIO", "Healthcare", "Managed Services"): "vendor risk management, compliance delegation, and audit support",
        ("CIO", "Fintech", "Managed Services"): "managed services governance, audit readiness, and vendor SLAs",
        ("CIO", "Technology", "Managed Services"): "strategic vendor partnerships and service level governance",
        ("CIO", "Retail", "Managed Services"): "managed services scalability and business continuity",
        ("CIO", "Manufacturing", "Managed Services"): "IT/OT managed services integration and vendor coordination",

        # VP Engineering + Managed Services
        ("VP Engineering", "Healthcare", "Managed Services"): "handoff processes, incident escalation, and team focus",
        ("VP Engineering", "Fintech", "Managed Services"): "managed services integration and engineering focus areas",
        ("VP Engineering", "Technology", "Managed Services"): "SRE partnership and reducing operational burden",
        ("VP Engineering", "Retail", "Managed Services"): "managed services during launches and campaigns",
        ("VP Engineering", "Manufacturing", "Managed Services"): "OT operations handoff and production support",

        # Engineering Manager + Managed Services
        ("Engineering Manager", "Healthcare", "Managed Services"): "on-call reduction and team focus on development",
        ("Engineering Manager", "Fintech", "Managed Services"): "incident response coordination and knowledge transfer",
        ("Engineering Manager", "Technology", "Managed Services"): "reduced operational burden and team productivity",
        ("Engineering Manager", "Retail", "Managed Services"): "campaign support and seasonal operations",
        ("Engineering Manager", "Manufacturing", "Managed Services"): "production support and shift coverage",
    }

    inputs = [
        HandleInput(
            name="role",
            display_name="Role",
            required=True,
            input_types=["Message", "Data"],
            info="Job title or role of the prospect. Valid values: CFO, CTO, CIO, VP Engineering, Engineering Manager, Other"
        ),
        HandleInput(
            name="industry",
            display_name="Industry",
            required=True,
            input_types=["Message", "Data"],
            info="Industry vertical of the prospect's company. Valid values: Healthcare, Fintech, Technology, Retail, Manufacturing, Other"
        ),
        HandleInput(
            name="service_type",
            display_name="Service Type",
            required=True,
            input_types=["Message", "Data"],
            info="CloudGeometry service the prospect is interested in. Valid values: AI Transformation, App Modernization, Cloud Migration, DevOps Acceleration, Data Platform, Managed Services"
        ),
    ]

    outputs = [
        Output(
            name="pain_point",
            display_name="Pain Point",
            method="map_pain_point",
        ),
    ]

    def _extract_value(self, value, key: str = None) -> str:
        """Extract text from a Message object, Data object, or return string as-is.

        Args:
            value: Can be Message, Data, dict, or string
            key: Optional key to extract from Data/dict objects
        """
        if value is None:
            return ""
        # Handle Message objects
        if hasattr(value, 'text'):
            return str(value.text).strip()
        # Handle Data objects (have .data attribute with dict)
        if hasattr(value, 'data') and isinstance(value.data, dict):
            if key and key in value.data:
                return str(value.data[key]).strip()
            # Return first value if no key specified
            for v in value.data.values():
                if isinstance(v, str):
                    return v.strip()
            return str(value.data).strip()
        # Handle dict
        if isinstance(value, dict):
            if key and key in value:
                return str(value[key]).strip()
            return str(value).strip()
        return str(value).strip()

    def map_pain_point(self) -> Data:
        """
        Map the role, industry, and service to a specific pain point.

        Returns:
            Data object containing the pain point and metadata
        """
        # Normalize inputs - handle Message objects, Data objects, and strings
        role = self._extract_value(self.role, "role") or "Other"
        industry = self._extract_value(self.industry, "industry") or "Other"
        service_type = self._extract_value(self.service_type, "service_type") or "Cloud Migration"

        # Look up pain point using 3-tuple key
        lookup_key = (role, industry, service_type)
        pain_point = self.PAIN_POINT_MATRIX.get(lookup_key)

        is_default = False
        if pain_point is None:
            # Generate dynamic default based on service type
            pain_point = f"cloud optimization and {service_type.lower()} best practices"
            is_default = True

        # Set status for UI feedback
        if is_default:
            self.status = f"Using default for {service_type}"
        else:
            self.status = f"{role} + {industry} + {service_type[:15]}..."

        return Data(data={
            "pain_point": pain_point,
            "role": role,
            "industry": industry,
            "service_type": service_type,
            "is_default": is_default,
            "lookup_key": f"{role}|{industry}|{service_type}"
        })
