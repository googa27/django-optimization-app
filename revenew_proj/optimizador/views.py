from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render

from .dataloader import DataLoader
from .forms import UploadForm
from .results import ResultsHandler
from .services import ProductionOptimizationService


optimization_service = ProductionOptimizationService()


def upload_view(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                csv_file = form.cleaned_data["csv_file"]
                params = DataLoader(csv_file).load()
                solution = optimization_service.solve(params).as_legacy_dict()
                result = ResultsHandler(solution, params).format()
                return render(request, "optimizador/results.html", {"result": result})
            except ValidationError as error:
                messages.error(request, str(error))
    else:
        form = UploadForm()

    return render(request, "optimizador/upload.html", {"form": form})
