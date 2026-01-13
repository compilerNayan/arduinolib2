#ifndef HTTP_REQUEST_DISPATCHER_H
#define HTTP_REQUEST_DISPATCHER_H

#include <unordered_map>
#include <NayanSerializer.h>
#include "EndpointTrie.h"
#include <StandardDefines.h>
#include <sstream>
#include <stdexcept>
#include <type_traits>
#include <algorithm>
#include <cctype>

#include "IHttpRequestDispatcher.h"

/// @Component
class HttpRequestDispatcher : public IHttpRequestDispatcher {

    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> getMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> postMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> putMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> patchMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> deleteMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> optionsMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> headMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> traceMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString)>> connectMappings;

    Private EndpointTrie endpointTrie;

    Public HttpRequestDispatcher() {
        InitializeMappings();
    }

    Public ~HttpRequestDispatcher() = default;

    Public StdString DispatchRequest(IHttpRequestPtr request) override {
        CStdString url = request->GetPath();
        CStdString payload = request->GetBody();
        EndpointMatchResult result = endpointTrie.Search(url);
        Val variables = result.variables;
        switch (request->GetMethod()) {
            case HttpMethod::GET:
                return getMappings[url](payload, variables);
            case HttpMethod::POST:
                return postMappings[url](payload, variables);
            case HttpMethod::PUT:
                return putMappings[url](payload, variables);
            case HttpMethod::PATCH:
                return patchMappings[url](payload, variables);
            case HttpMethod::DELETE:
                return deleteMappings[url](payload, variables);
            case HttpMethod::OPTIONS:
                return optionsMappings[url](payload, variables);
            case HttpMethod::HEAD:
                return headMappings[url](payload, variables);
            case HttpMethod::TRACE:
                return traceMappings[url](payload, variables);
            case HttpMethod::CONNECT:
                return connectMappings[url](payload, variables);
        } 
        return StdString();
    }

    Private Void InitializeMappings() {

    }

    /**
     * Template function to convert a string to a given type.
     * 
     * - If Type is string-related (StdString, CStdString, std::string, string), returns as-is
     * - If Type is a primitive type (int, Int, long, Long, float, double, bool, etc.), converts from string
     * - Handles types from StandardDefines.h (Int, Long, UInt, ULong, Bool, etc.)
     * 
     * @tparam Type The target type to convert to
     * @param str The input string to convert
     * @return The converted value of type Type
     */
    template<typename Type>
    Type ConvertToType(CStdString str) {
        // Handle string types - return as-is
        if constexpr (std::is_same_v<Type, StdString> || 
                      std::is_same_v<Type, CStdString> ||
                      std::is_same_v<Type, std::string> ||
                      std::is_same_v<Type, const std::string>) {
            return StdString(str);
        }
        // Handle boolean types (bool, Bool, CBool)
        else if constexpr (std::is_same_v<Type, bool> || 
                          std::is_same_v<Type, Bool> || 
                          std::is_same_v<Type, CBool>) {
            StdString lower = str;
            std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
            if (lower == "true" || lower == "1") {
                return true;
            } else if (lower == "false" || lower == "0") {
                return false;
            } else {
                throw std::invalid_argument("Invalid boolean value: " + StdString(str));
            }
        }
        // Handle signed integer types (int, Int, CInt, long, Long, CLong, etc.)
        else if constexpr (std::is_integral_v<Type> && std::is_signed_v<Type>) {
            try {
                if constexpr (sizeof(Type) <= sizeof(int)) {
                    return static_cast<Type>(std::stoi(str));
                } else if constexpr (sizeof(Type) <= sizeof(long)) {
                    return static_cast<Type>(std::stol(str));
                } else {
                    return static_cast<Type>(std::stoll(str));
                }
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid signed integer value: " + StdString(str));
            }
        }
        // Handle unsigned integer types (unsigned int, UInt, CUInt, unsigned long, ULong, CULong, etc.)
        else if constexpr (std::is_integral_v<Type> && std::is_unsigned_v<Type>) {
            try {
                if constexpr (sizeof(Type) <= sizeof(unsigned int)) {
                    return static_cast<Type>(std::stoul(str));
                } else if constexpr (sizeof(Type) <= sizeof(unsigned long)) {
                    return static_cast<Type>(std::stoul(str));
                } else {
                    return static_cast<Type>(std::stoull(str));
                }
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid unsigned integer value: " + StdString(str));
            }
        }
        // Handle floating point types (float, double, long double)
        else if constexpr (std::is_floating_point_v<Type>) {
            try {
                if constexpr (std::is_same_v<Type, float>) {
                    return std::stof(str);
                } else if constexpr (std::is_same_v<Type, double>) {
                    return std::stod(str);
                } else {
                    return std::stold(str);
                }
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid floating point value: " + StdString(str));
            }
        }
        // Handle character types (char, Char, CChar, unsigned char, UChar, CUChar, UInt8)
        else if constexpr (std::is_same_v<Type, char> || 
                          std::is_same_v<Type, Char> || 
                          std::is_same_v<Type, CChar> ||
                          std::is_same_v<Type, unsigned char> || 
                          std::is_same_v<Type, UChar> || 
                          std::is_same_v<Type, CUChar> ||
                          std::is_same_v<Type, UInt8>) {
            if (str.length() == 1) {
                return static_cast<Type>(str[0]);
            } else if (str.length() == 0) {
                return static_cast<Type>(0);
            } else {
                // Try to parse as integer for character types
                try {
                    return static_cast<Type>(std::stoi(str));
                } catch (const std::exception& e) {
                    throw std::invalid_argument("Invalid character value: " + StdString(str));
                }
            }
        }
        // Fallback: try to use stringstream for other types
        else {
            std::istringstream iss(str);
            Type value;
            if (!(iss >> value)) {
                throw std::invalid_argument("Cannot convert string to type: " + StdString(str));
            }
            return value;
        }
    }

};

#endif // HTTP_REQUEST_DISPATCHER_H