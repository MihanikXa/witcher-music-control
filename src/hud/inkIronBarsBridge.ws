// Original private-test adapter. Install only with the single I&I bars movie.
// SAHUD keeps its context policies, timers, visibility and data consumers.
// Its alternate painters and native-child toxicity split cannot control the
// I&I composite Shape. Use the combined status policy for this first proof.
// These are in-memory values: no configuration or profile file is written.
@wrapMethod(SahSettings)
function Load()
{
    wrappedMethod();
    hudStyle = 0;
    hudMinimal = false;
    toxicMode = 0;
}
