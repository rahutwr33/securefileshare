# Step 1: Use official node image as the base image
FROM node:20 AS build

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy package.json and package-lock.json to install dependencies
COPY ./client/package*.json ./

# Step 4: Install dependencies
RUN npm install

# Step 5: Copy the entire project files to the container
COPY ./client ./

# Step 6: Build the production version of the React app
RUN npm run build

# Step 7: Use Nginx to serve the build files
FROM nginx:alpine

# Copy the nginx configuration file (ensure you have nginx.conf in the root)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Step 8: Copy the build output to the Nginx container
COPY --from=build /app/dist /usr/share/nginx/html

# Step 9: Expose port 80 for the React app
EXPOSE 80

# Step 10: Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
