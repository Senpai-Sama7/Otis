"""
OpenTelemetry distributed tracing configuration.

Provides flame graph visualization of agent execution.
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def configure_tracing(app=None):
    """
    Configure OpenTelemetry tracing with Jaeger exporter.

    Args:
        app: FastAPI application instance (optional)
    """
    try:
        # Create resource with service name
        resource = Resource(attributes={SERVICE_NAME: settings.app_name})

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Configure Jaeger exporter
        jaeger_host = getattr(settings, "jaeger_host", "localhost")
        jaeger_port = getattr(settings, "jaeger_port", 6831)

        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )

        # Add span processor
        processor = BatchSpanProcessor(jaeger_exporter)
        provider.add_span_processor(processor)

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        # Instrument FastAPI if app provided
        if app:
            FastAPIInstrumentor.instrument_app(app)

        # Instrument httpx for LLM calls
        HTTPXClientInstrumentor().instrument()

        logger.info(
            "tracing.configured",
            service=settings.app_name,
            jaeger_host=jaeger_host,
            jaeger_port=jaeger_port,
        )

    except Exception as e:
        logger.error("tracing.configuration_failed", error=str(e))


def get_tracer(name: str):
    """
    Get a tracer instance.

    Args:
        name: Tracer name (usually __name__)

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def trace_agent_execution(func):
    """
    Decorator to trace agent execution with spans.

    Usage:
        @trace_agent_execution
        async def run_agent(...):
            ...
    """
    import functools

    from opentelemetry import trace

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(f"agent.{func.__name__}") as span:
            # Add attributes
            span.set_attribute("agent.function", func.__name__)
            if args:
                span.set_attribute("agent.args_count", len(args))
            if kwargs:
                span.set_attribute("agent.kwargs_count", len(kwargs))

            try:
                result = await func(*args, **kwargs)
                span.set_attribute("agent.success", True)
                return result
            except Exception as e:
                span.set_attribute("agent.success", False)
                span.set_attribute("agent.error", str(e))
                span.record_exception(e)
                raise

    return wrapper


def trace_tool_execution(tool_name: str):
    """
    Decorator to trace tool execution.

    Usage:
        @trace_tool_execution("scan_environment")
        async def execute(...):
            ...
    """
    import functools

    from opentelemetry import trace

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(f"tool.{tool_name}") as span:
                span.set_attribute("tool.name", tool_name)

                # Add parameters as attributes
                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float, bool)):
                        span.set_attribute(f"tool.param.{key}", value)

                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("tool.success", result.get("success", False))
                    return result
                except Exception as e:
                    span.set_attribute("tool.success", False)
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


def trace_policy_validation(func):
    """
    Decorator to trace policy validation.

    Usage:
        @trace_policy_validation
        def validate(...):
            ...
    """
    import functools

    from opentelemetry import trace

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("policy.validate") as span:
            tool_name = kwargs.get("tool_name", "unknown")
            span.set_attribute("policy.tool", tool_name)

            try:
                decision = func(*args, **kwargs)
                span.set_attribute("policy.decision", decision.value)
                return decision
            except Exception as e:
                span.record_exception(e)
                raise

    return wrapper


def trace_llm_call(func):
    """
    Decorator to trace LLM inference calls.

    Usage:
        @trace_llm_call
        async def generate(...):
            ...
    """
    import functools

    from opentelemetry import trace

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("llm.generate") as span:
            prompt = kwargs.get("prompt", "")
            span.set_attribute("llm.prompt_length", len(prompt))
            span.set_attribute("llm.temperature", kwargs.get("temperature", 0.7))
            span.set_attribute("llm.max_tokens", kwargs.get("max_tokens", 0))

            try:
                result = await func(*args, **kwargs)
                span.set_attribute("llm.response_length", len(result) if result else 0)
                return result
            except Exception as e:
                span.record_exception(e)
                raise

    return wrapper
