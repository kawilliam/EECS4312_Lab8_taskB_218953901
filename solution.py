## Student Name: Kyle Williamson
## Student ID: 218953901
"""
Task: Event Registration with Waitlist (Lab 9 Updated)

Updates from Lab 9 persona-based constraints:
- C4/FR20: All rejections now return a reason message via exception text.
- C5/FR21: cancel() now returns a result dict confirming success and any promotion.
- C3/FR22: Exactly one response per operation. Promoted user status only visible via status().
- C4/FR23: cancel() includes promotion explanation in its return value.
- FR9: Valid states are explicitly "registered", "waitlisted", "none".
- FR13: Re-registering user joins end of waitlist as a new user.
- FR15: Promotion happens atomically within cancel().
- FR16: User cannot exist in both lists simultaneously.
- A1: user_id comparisons are case-sensitive.
- A9: Negative capacity rejected with ValueError.
"""

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation (if required by handout)."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Students must implement this class per the lab handout.
    Deterministic ordering is required (e.g., FIFO waitlist, predictable registration order).
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self.capacity = capacity
        self.registered: List[str] = []  
        self.waitlist: List[str] = []     

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        if user_id in self.registered or user_id in self.waitlist:
            raise DuplicateRequest(
                f"Registration rejected: '{user_id}' is already in the system. "
                f"A user may not register more than once."
            )
        
        if len(self.registered) < self.capacity:
            self.registered.append(user_id)
            return UserStatus("registered")
        
        self.waitlist.append(user_id)
        return UserStatus("waitlisted",len(self.waitlist))

    def cancel(self, user_id: str) -> dict:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlist
          - behavior when user not found depends on handout (raise NotFound or ignore)

        Raises:
            NotFound (if required by handout)
        """
        if not (user_id in self.registered or user_id in self.waitlist):
            raise NotFound(
                f"Cancellation rejected: '{user_id}' was not found in the system. "
                f"No action was taken."
            )
        promoted_user = None
        if user_id in self.registered:
            self.registered.remove(user_id)
            if self.waitlist:
                promoted_user = self.waitlist.pop(0)
                self.registered.append(promoted_user)
        elif user_id in self.waitlist:
            self.waitlist.remove(user_id)

        if promoted_user:
            message = (
                f"'{user_id}' has been removed from registered. "
                f"'{promoted_user}' has been automatically promoted from the waitlist."
            )
        else:
            message = f"'{user_id}' has been successfully removed from the system."

        return {
            "cancelled": user_id,
            "promoted": promoted_user,
            "message": message
        }
        

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        if user_id in self.registered:
            return UserStatus("registered")
        if user_id in self.waitlist:
            position = self.waitlist.index(user_id) + 1
            return UserStatus("waitlisted", position)
        return UserStatus("none")

    def snapshot(self) -> dict:
        """
        (Optional helper for debugging/tests)
        Return a deterministic snapshot of internal state.
        """
        return {
            "capacity": self.capacity,
            "registered": list(self.registered),  
            "waitlist": list(self.waitlist)      
        }