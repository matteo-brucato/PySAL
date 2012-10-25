PYTHON=python


all: butterfly hypercube mesh shuffle pram

butterfly: out_BUTTERFLY.py
out_BUTTERFLY.py: algorithms/BUTTERFLY.pysal.py synchronous_unshared.py pysal.py
	$(PYTHON) pysal.py algorithms/BUTTERFLY.pysal.py

hypercube: out_HYPERCUBE.py
out_HYPERCUBE.py: algorithms/HYPERCUBE.pysal.py synchronous_unshared.py pysal.py
	$(PYTHON) pysal.py algorithms/HYPERCUBE.pysal.py

mesh: out_MESH.py
out_MESH.py: algorithms/MESH.pysal.py synchronous_unshared.py pysal.py
	$(PYTHON) pysal.py algorithms/MESH.pysal.py

shuffle: out_SHUFFLE.py
out_SHUFFLE.py: algorithms/SHUFFLE.pysal.py synchronous_unshared.py pysal.py
	$(PYTHON) pysal.py algorithms/SHUFFLE.pysal.py

pram: out_PRAM.py
out_PRAM.py: algorithms/PRAM.pysal.py synchronous_shared.py pysal.py
	$(PYTHON) pysal.py algorithms/PRAM.pysal.py


tests: butterfly hypercube mesh shuffle pram
	$(PYTHON) out_BUTTERFLY.py && \
	$(PYTHON) out_HYPERCUBE.py && \
	$(PYTHON) out_MESH.py && \
	$(PYTHON) out_SHUFFLE.py && \
	$(PYTHON) out_PRAM.py

clean:
	pyclean .
	rm out_*.py
