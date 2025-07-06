from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.contrib import messages

from .forms import UploadForm
from .dataloader import DataLoader
from .optimizer import OptimizationModel
from .results import ResultsHandler

# Create your views here.


def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # --- STEP 1: Load and validate uploaded CSV ---
                csv_file = request.FILES['csv_file']
                loader = DataLoader(csv_file)
                params = loader.load()

                # --- STEP 2: Solve the optimization problem ---
                model = OptimizationModel(params)
                solution = model.solve()

                # --- STEP 3: Format the result for display ---
                formatter = ResultsHandler(solution)
                result = formatter.format()

                # --- STEP 4: Render the results page ---
                return render(request, 'optimizador/results.html', {
                    'result': result
                })

            except ValidationError as e:
                messages.error(request, str(e))

    else:
        form = UploadForm()

    return render(request, 'optimizador/upload.html', {'form': form})
