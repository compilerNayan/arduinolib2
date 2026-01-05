#ifndef HTTP_REQUEST_DISPATCHER_H
#define HTTP_REQUEST_DISPATCHER_H

#include <unordered_map>
#include <NayanSerializer.h>
#include <iostream>

#include "IHttpRequestDispatcher.h"
#include "HttpMethod.h"

/// @Component
class HttpRequestDispatcher : public IHttpRequestDispatcher {

    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> getMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> postMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> putMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> patchMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> deleteMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> optionsMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> headMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> traceMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> connectMappings;

    Public HttpRequestDispatcher() {
        InitializeMappings();
    }

    Public ~HttpRequestDispatcher() = default;

    Public StdString DispatchRequest(IHttpRequestPtr request) override {
        CStdString url = request->GetPath();
        CStdString payload = request->GetBody();
        
        std::cout << "[HttpRequestDispatcher] DispatchRequest() called for URL: '" << url << "', Method: " << MethodToString(request->GetMethod()) << std::endl;
        
        std::function<StdString(CStdString)> handler;
        Bool found = false;
        
        switch (request->GetMethod()) {
            case HttpMethod::GET:
                if (getMappings.find(StdString(url)) != getMappings.end()) {
                    handler = getMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::POST:
                if (postMappings.find(StdString(url)) != postMappings.end()) {
                    handler = postMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::PUT:
                if (putMappings.find(StdString(url)) != putMappings.end()) {
                    handler = putMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::PATCH:
                if (patchMappings.find(StdString(url)) != patchMappings.end()) {
                    handler = patchMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::DELETE:
                if (deleteMappings.find(StdString(url)) != deleteMappings.end()) {
                    handler = deleteMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::OPTIONS:
                if (optionsMappings.find(StdString(url)) != optionsMappings.end()) {
                    handler = optionsMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::HEAD:
                if (headMappings.find(StdString(url)) != headMappings.end()) {
                    handler = headMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::TRACE:
                if (traceMappings.find(StdString(url)) != traceMappings.end()) {
                    handler = traceMappings[StdString(url)];
                    found = true;
                }
                break;
            case HttpMethod::CONNECT:
                if (connectMappings.find(StdString(url)) != connectMappings.end()) {
                    handler = connectMappings[StdString(url)];
                    found = true;
                }
                break;
        }
        
        if (found && handler) {
            std::cout << "[HttpRequestDispatcher] Handler found for URL: '" << url << "', calling handler..." << std::endl;
            StdString result = handler(payload);
            std::cout << "[HttpRequestDispatcher] Handler returned result length: " << result.length() << std::endl;
            return result;
        }
        
        // No handler found for this URL/method combination
        std::cout << "[HttpRequestDispatcher] WARNING: No handler found for URL: '" << url << "', Method: " << MethodToString(request->GetMethod()) << std::endl;
        return StdString("{\"error\":\"Not Found\",\"message\":\"No handler found for " + StdString(url) + "\"}");
    }

    Private Void InitializeMappings() {

    }

};

#endif // HTTP_REQUEST_DISPATCHER_H