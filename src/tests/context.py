"""
Task context management for providing background information to agents.
"""
from typing import Dict, Any, Optional


class TaskContext:
    """
    Manages task context that provides background information to agents
    during evaluation.
    """

    def __init__(
        self,
        task_description: str,
        success_criteria: Optional[str] = None,
        target_audience: Optional[str] = None,
        domain: Optional[str] = None,
        constraints: Optional[str] = None,
        **additional_context
    ):
        """
        Initialize task context.

        Args:
            task_description: Description of what the chat API should accomplish
            success_criteria: What makes a good response
            target_audience: Who the responses are for
            domain: Domain or industry context
            constraints: Any constraints or requirements
            **additional_context: Any additional context fields
        """
        self.task_description = task_description
        self.success_criteria = success_criteria
        self.target_audience = target_audience
        self.domain = domain
        self.constraints = constraints
        self.additional_context = additional_context

    def to_text(self) -> str:
        """
        Convert context to readable text format for agents.

        Returns:
            Formatted context text
        """
        parts = [f"Task: {self.task_description}"]

        if self.target_audience:
            parts.append(f"Target Audience: {self.target_audience}")

        if self.domain:
            parts.append(f"Domain: {self.domain}")

        if self.success_criteria:
            parts.append(f"Success Criteria: {self.success_criteria}")

        if self.constraints:
            parts.append(f"Constraints: {self.constraints}")

        # Add any additional context
        for key, value in self.additional_context.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                parts.append(f"{formatted_key}: {value}")

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary.

        Returns:
            Context as dict
        """
        return {
            "task_description": self.task_description,
            "success_criteria": self.success_criteria,
            "target_audience": self.target_audience,
            "domain": self.domain,
            "constraints": self.constraints,
            **self.additional_context
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskContext":
        """
        Create TaskContext from dictionary.

        Args:
            data: Context data dict

        Returns:
            TaskContext instance
        """
        # Extract known fields
        task_description = data.pop("task_description", "")
        success_criteria = data.pop("success_criteria", None)
        target_audience = data.pop("target_audience", None)
        domain = data.pop("domain", None)
        constraints = data.pop("constraints", None)

        # Everything else is additional context
        return cls(
            task_description=task_description,
            success_criteria=success_criteria,
            target_audience=target_audience,
            domain=domain,
            constraints=constraints,
            **data
        )

    def __str__(self) -> str:
        return self.to_text()

    def __repr__(self) -> str:
        return f"TaskContext(task_description='{self.task_description[:50]}...')"


class ContextBuilder:
    """Helper class for building task contexts"""

    @staticmethod
    def build_customer_support_context(
        product: str,
        tone: str = "friendly and helpful"
    ) -> TaskContext:
        """
        Build context for customer support evaluation.

        Args:
            product: Product name
            tone: Expected tone

        Returns:
            TaskContext for customer support
        """
        return TaskContext(
            task_description=f"Provide customer support for {product}",
            target_audience="Customers seeking help",
            success_criteria=f"Clear, accurate answers with a {tone} tone",
            domain="Customer Support"
        )

    @staticmethod
    def build_technical_docs_context(
        technology: str,
        audience_level: str = "intermediate"
    ) -> TaskContext:
        """
        Build context for technical documentation evaluation.

        Args:
            technology: Technology being documented
            audience_level: Technical level (beginner/intermediate/advanced)

        Returns:
            TaskContext for technical docs
        """
        return TaskContext(
            task_description=f"Provide technical documentation for {technology}",
            target_audience=f"{audience_level.capitalize()} developers",
            success_criteria="Clear explanations with code examples where appropriate",
            domain="Technical Documentation",
            constraints="Use precise technical terminology"
        )

    @staticmethod
    def build_sales_context(
        product: str,
        value_proposition: str
    ) -> TaskContext:
        """
        Build context for sales conversation evaluation.

        Args:
            product: Product being sold
            value_proposition: Key value proposition

        Returns:
            TaskContext for sales
        """
        return TaskContext(
            task_description=f"Engage in sales conversation about {product}",
            target_audience="Potential customers",
            success_criteria="Persuasive, builds trust, addresses objections",
            domain="Sales",
            value_proposition=value_proposition
        )

    @staticmethod
    def build_education_context(
        subject: str,
        grade_level: str
    ) -> TaskContext:
        """
        Build context for educational content evaluation.

        Args:
            subject: Subject being taught
            grade_level: Grade or education level

        Returns:
            TaskContext for education
        """
        return TaskContext(
            task_description=f"Teach {subject} concepts",
            target_audience=f"{grade_level} students",
            success_criteria="Clear explanations, engaging, pedagogically sound",
            domain="Education",
            constraints="Age-appropriate language and examples"
        )
