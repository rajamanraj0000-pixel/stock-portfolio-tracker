from fastapi import HTTPException, status

class PortfolioNotFoundError(HTTPException):
    def __init__(self, portfolio_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found"
        )

class InsufficientSharesError(HTTPException):
    def __init__(self, symbol: str, available: float, requested: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient shares for {symbol}. Available: {available}, Requested: {requested}"
        )

class InvalidStockSymbolError(HTTPException):
    def __init__(self, symbol: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock symbol '{symbol}' not found or invalid"
        )

class InsufficientCashError(HTTPException):
    def __init__(self, required: float, available: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient cash. Required: ${required:.2f}, Available: ${available:.2f}"
        )