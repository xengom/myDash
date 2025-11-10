"""Widgets package for myDash."""

from src.widgets.portfolio_table import PortfolioTable
from src.widgets.stock_modal import AddStockModal, EditStockModal, DeleteConfirmModal
from src.widgets.portfolio_modal import AddPortfolioModal, EditPortfolioModal
from src.widgets.google_panel import GooglePanel
from src.widgets.chart_view import ChartView

__all__ = [
    "PortfolioTable",
    "AddStockModal",
    "EditStockModal",
    "DeleteConfirmModal",
    "AddPortfolioModal",
    "EditPortfolioModal",
    "GooglePanel",
    "ChartView",
]
