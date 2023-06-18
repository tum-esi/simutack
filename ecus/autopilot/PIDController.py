
from Logger import logger


class PIDController:

    def __init__(self, kp: float = 0.0, ki: float = 0.0, kd: float = 0.0, dt: float = 1.0):
        # PID controller settings
        self.Kp = kp    # Proportional gain
        self.Ki = ki    # Integral gain
        self.Kd = kd    # Differential gain

        # Control update rate (= sensor input update rate)
        self.dt = dt

        # Derivative low-pass filter time constant
        self.tau = 1.0
        self.integrator = 0.0
        self.differentiator = 0.0
        self.last_error = 0.0
        self.last_measurement = 0.0

    def update(self, measurement, error):
        # Proportional term
        p = self.Kp * error

        # Integral term
        i = self.integrator + (0.5 * self.Ki *
                               self.dt * (self.last_error + error))

        # Derivative term
        d = (2.0 * self.Kd * (measurement - self.last_measurement) + (2.0 *
             self.tau - self.dt) * self.differentiator) / (2.0 * self.tau + self.dt)

        # Debug output
        logger.debug(f"P: {p}, I: {i}, D: {d}")

        # Compute actual PID controller output (clamp value to limits)
        pid_response = min(max(p + i + d, -1.0), 1.0)

        # Update state variables
        self.integrator = i
        self.differentiator = d
        self.last_error = error
        self.last_measurement = measurement

        # Return response
        return pid_response


    def reset(self):
        # Reset PID variables
        self.integrator = 0.0
        self.differentiator = 0.0
        self.last_error = 0.0
        self.last_measurement = 0.0
