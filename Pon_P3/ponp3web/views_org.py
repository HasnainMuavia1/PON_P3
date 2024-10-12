import io

from django.shortcuts import render, HttpResponse, redirect
from .models import data,Counter
import csv
import pandas as pd
from django.core.mail import EmailMessage
import os
from django.db import transaction


def index(request):
    return render(request, 'index.html')


# Create your views here.
def input(request):
    if request.method == 'POST':
        counter, created = Counter.objects.get_or_create(pk=1)  # Assuming a single counter instance
        counter.increment()
        print('hello')
        text = request.POST.get('te')
        file = request.FILES.get('csv_data')
        print(file)
        email = request.POST['e']
        if not text:
            # if the file is excel file then convert into csv
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                file = pd.read_excel(file)
                print(file.head())
                csv_file = file.to_csv(index=False)
            result = handle_uploaded_file2(file, email)
            if result == 'Error':
                return render(request, 'input_Prediction.html', {'msg': 'Wrong format or one of the keys is missing','counter':Counter.objects.first()})
            else:
                return render(request, 'input_Prediction.html', {'msg': 'Email sent successfully! Check your email','counter':Counter.objects.first()})
        elif not file:
            result = get_values_combine(text, email)
            if result == 'Error':
                return render(request, 'input_Prediction.html', {'msg': 'Failed to send email','counter':Counter.objects.first()})
            else:
                return render(request, 'input_Prediction.html', {'msg': 'Email sent successfully! Check your email','counter':Counter.objects.first()})

    return render(request, 'input_Prediction.html',{'counter':Counter.objects.first()})


def handle_uploaded_file2(file, email):
    """
    Process the uploaded CSV file and create a combined CSV file based on filtered data.
    """
    # Define required keys as a set
    required_keys = {'refseq_ids', 'variation_ids'}

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file)

    # Get the DataFrame columns as a set
    actual_columns = set(df.columns)

    # Check if all required keys are in the actual columns
    if required_keys.issubset(actual_columns):
        # Group by 'refseq_ids'
        grouped = df.groupby('refseq_ids')

        # List to store combined data
        combined_data = []

        # Process each group
        for var1, group in grouped:
            var2_list = group['variation_ids'].tolist()
            var2_list = [k.upper() for k in var2_list]
            print(var1)
            print(var2_list)

            # Query the database
            if var2_list:
                results = data.objects.filter(refseq_ids=var1, variation_ids__in=var2_list)
            else:
                results = data.objects.filter(refseq_ids=var1)

            # Convert the results to a list of dictionaries
            data_list = list(results.values('refseq_ids', 'variation_ids', 'meanProb', 'stdProb', 'pred_label'))
            combined_data.extend(data_list)

        # Convert the combined data list to a DataFrame
        combined_df = pd.DataFrame(combined_data)
        combined_df.drop_duplicates(subset=['refseq_ids', 'variation_ids'], inplace=True)

        # Create a CSV file from the combined DataFrame
        csv_buffer = io.StringIO()
        combined_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Go to the start of the StringIO buffer

        # Send the email with CSV attachment
        email_message = EmailMessage(
            'Predictions for your uploaded file are ready.',
            'Upon the usage the users are requested to use the following citation(s):',
            'Thank you for using our webserver',
            'Protein Structure and Bioinformatics Group - Lund University.',
            to=[email]
        )
        email_message.attach('combined_data.csv', csv_buffer.getvalue(), 'text/csv')
        email_message.send()
        return 'success'
    else:
        # If the required keys are not present, return an error message
        return 'Error'


def get_values_combine(text, email):
    blocks = text.split('>')
    # Initialize an empty list to accumulate all DataFrames
    combined_data = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        if lines:
            var1 = lines[0].strip()
            var2_list = [item.strip().upper() for item in lines[1:] if item.strip()]

            # Query the database
            if var2_list:
                results = data.objects.filter(refseq_ids=var1, variation_ids__in=var2_list)
            else:
                results = data.objects.filter(refseq_ids=var1, variation_ids__in=var2_list)

            # Convert the results to pandas DataFrame and append to the list
            data_list = list(results.values('refseq_ids', 'variation_ids', 'meanProb', 'stdProb', 'pred_label'))
            combined_data.extend(data_list)

    # Convert the combined data list to a DataFrame
    combined_df = pd.DataFrame(combined_data)
    combined_df.drop_duplicates(subset=['refseq_ids', 'variation_ids'], inplace=True)
    # Create a CSV file from the combined DataFrame
    csv_buffer = io.StringIO()
    combined_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  # Go to the start of the StringIO buffer

    # Send the email with CSV attachment
    try:
        email_message = EmailMessage(
            'Predictions for your uploaded file are ready.',
            'Upon the usage the users are requested to use the following citation(s):',
            'Thank you for using our webserver',
            'Protein Structure and Bioinformatics Group - Lund University.',
            to=[email]
        )
        email_message.attach('combined_data.csv', csv_buffer.getvalue(), 'text/csv')
        email_message.send()
    except:
        return 'Error'


def upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for f in files:
            process_csv(f)
        return render(request, 'upload.html',{'msg':"Upload Successfully !"})

    return render(request, 'upload.html')


def process_csv(csv_file, batch_size=10000):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # List to hold all the objects to be created
    objects_to_create = []

    # Iterate over the rows of the DataFrame and prepare to save to the database if not duplicate
    for _, row in df.iterrows():
        # Check for duplication based on refseq_ids and variation_ids
        if not data.objects.filter(refseq_ids=row['refseq_ids'], variation_ids=row['variation_ids']).exists():
            objects_to_create.append(data(
                refseq_ids=row['refseq_ids'],
                variation_ids=row['variation_ids'],
                meanProb=row['meanProb'],
                stdProb=row['standardDev'],
                pred_label=row['Pred_label']
            ))

        # Bulk create objects in batches
        if len(objects_to_create) >= batch_size:
            with transaction.atomic():
                data.objects.bulk_create(objects_to_create)
            objects_to_create = []

    # Create any remaining objects
    if objects_to_create:
        with transaction.atomic():
            data.objects.bulk_create(objects_to_create)


def about(request):
    return render(request, 'about.html')


def disclaimer(request):
    return render(request, 'disclaimer.html')
