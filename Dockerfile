# Gunakan image dasar Python
FROM python:3.9

# Setel direktori kerja
WORKDIR /app

# Salin requirements.txt dan install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Salin semua file ke direktori kerja
COPY . .

# Tentukan command untuk menjalankan aplikasi
CMD ["gunicorn", "-b", "0.0.0.0:8080", "server:app"]

# Expose port 8080
EXPOSE 8080
