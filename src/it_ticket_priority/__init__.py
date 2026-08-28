"""Hybrid AI/ML service-desk priority and copilot package."""

from .copilot import ServiceDeskCopilot
from .inference import TicketPriorityPredictor

__all__ = ["ServiceDeskCopilot", "TicketPriorityPredictor"]
__version__ = "2.0.0"
