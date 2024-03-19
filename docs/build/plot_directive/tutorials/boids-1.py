from vivarium import InteractiveContext
from vivarium.examples.boids import Population, Location, plot_birds

sim = InteractiveContext(components=[Population(), Location()])
plot_birds(sim, plot_velocity=True)